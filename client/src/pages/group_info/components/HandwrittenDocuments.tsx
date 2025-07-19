import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../../auth/AuthProvider';
import { Button, List, Upload, message, Typography, Card, Space, Popconfirm, Tag } from 'antd';
import type { RcFile, UploadProps } from 'antd/es/upload';
import { 
    uploadHandwrittenDocument, 
    listHandwrittenDocuments, 
    getHandwrittenStatus,
    downloadProcessedDocument,
    deleteHandwrittenDocument,
    HandwrittenDocument,
    HandwrittenListResponse 
} from '../../../services/handwrittenApi';
import { FileTextOutlined, DownloadOutlined, DeleteOutlined, SyncOutlined } from '@ant-design/icons';

export function HandwrittenDocuments() {
    const { groupId } = useParams<{ groupId: string }>();
    const auth = useAuth();

    const [documents, setDocuments] = useState<HandwrittenListResponse>({ processing: [], completed: [] });
    const [loading, setLoading] = useState<boolean>(false);
    const [uploading, setUploading] = useState<boolean>(false);

    const fetchDocuments = async (): Promise<void> => {
        if (!groupId || !auth.token) return;
        
        setLoading(true);
        try {
            const data = await listHandwrittenDocuments(groupId, auth.token);
            setDocuments(data);
        } catch (error: any) {
            message.error(error.message || 'Failed to fetch handwritten documents');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, [groupId]);

    // Separate effect for polling that doesn't recreate intervals unnecessarily
    useEffect(() => {
        const interval = setInterval(() => {
            if (documents.processing.length > 0) {
                checkProcessingStatus();
            }
        }, 5000); // Check every 5 seconds

        return () => clearInterval(interval);
    }, [documents.processing.length, auth.token]);

    const checkProcessingStatus = async () => {
        if (!auth.token) return;

        let statusChanged = false;
        for (const doc of documents.processing) {
            try {
                const status = await getHandwrittenStatus(doc.task_id, auth.token);
                if (status.status !== 'PENDING') {
                    statusChanged = true;
                    break; // Exit early if any status changed
                }
            } catch (error) {
                console.error(`Failed to check status for ${doc.task_id}:`, error);
            }
        }
        
        // Only refresh if status actually changed
        if (statusChanged) {
            fetchDocuments();
        }
    };

    const handleUpload = async (file: RcFile) => {
        if (!groupId || !auth.token) {
            message.error("Cannot upload file: missing group ID or auth token.");
            return;
        }

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            message.error("Only PDF files are supported for handwritten document processing.");
            return;
        }

        setUploading(true);
        try {
            const response = await uploadHandwrittenDocument(groupId, file, auth.token);
            message.success(`Document "${file.name}" uploaded for handwritten processing. Task ID: ${response.task_id}`);
            fetchDocuments(); // Refresh the list
        } catch (error: any) {
            message.error(error.message || "Failed to upload handwritten document.");
        } finally {
            setUploading(false);
        }
    };

    const handleDownload = async (doc: HandwrittenDocument) => {
        if (!auth.token || !groupId) return;
        
        try {
            const filename = doc.processed_filename || `processed_${doc.original_filename}`;
            await downloadProcessedDocument(doc.task_id, groupId, auth.token, filename);
            message.success(`Downloaded ${filename}`);
        } catch (error: any) {
            message.error(error.message || 'Failed to download processed document');
        }
    };

    const handleDelete = async (taskId: string) => {
        if (!auth.token) return;

        try {
            await deleteHandwrittenDocument(taskId, auth.token);
            message.success('Document deleted successfully');
            fetchDocuments(); // Refresh the list
        } catch (error: any) {
            message.error(error.message || 'Failed to delete document');
        }
    };

    const getStatusTag = (status: string, errorMessage?: string) => {
        switch (status) {
            case 'PENDING':
                return <Tag icon={<SyncOutlined spin />} color="blue">Processing</Tag>;
            case 'SUCCESS':
                return <Tag color="green">Completed</Tag>;
            case 'FAILURE':
                return <Tag color="red" title={errorMessage}>Failed</Tag>;
            default:
                return <Tag color="default">{status}</Tag>;
        }
    };

    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleString();
    };

    const uploadProps: UploadProps = {
        beforeUpload: (file: RcFile) => {
            handleUpload(file as RcFile);
            return false;
        },
        showUploadList: false,
        disabled: uploading,
        accept: '.pdf',
    };

    return (
        <div style={{ padding: 16 }}>
            <Card style={{ marginBottom: 24 }}>
                <Typography.Title level={4}>📝 Handwritten Document Processing</Typography.Title>
                <Typography.Paragraph>
                    Upload handwritten PDF documents to convert them to LaTeX format. 
                    The AI will extract text from your handwritten notes and create a properly formatted LaTeX document.
                </Typography.Paragraph>
                
                <Space direction="vertical" style={{ width: '100%' }}>
                    <Upload {...uploadProps}>
                        <Button 
                            type="primary" 
                            size="large" 
                            loading={uploading} 
                            disabled={!auth.token}
                            icon={<FileTextOutlined />}
                        >
                            📤 Upload Handwritten PDF
                        </Button>
                    </Upload>

                    {documents.processing.length > 0 && (
                        <>
                            <Typography.Text strong>
                                🔄 Processing Documents ({documents.processing.length}):
                            </Typography.Text>
                            <List
                                loading={loading}
                                dataSource={documents.processing}
                                locale={{ emptyText: "No documents currently processing" }}
                                renderItem={(doc: HandwrittenDocument) => (
                                    <List.Item key={doc.task_id} actions={[
                                        <Popconfirm
                                            key="delete"
                                            title="Delete document?"
                                            description={`Delete "${doc.original_filename}"? This action cannot be undone.`}
                                            onConfirm={() => handleDelete(doc.task_id)}
                                            okText="Yes, Delete"
                                            cancelText="Cancel"
                                        >
                                            <Button danger size="small" icon={<DeleteOutlined />}>
                                                Delete
                                            </Button>
                                        </Popconfirm>
                                    ]}>
                                        <List.Item.Meta
                                            title={
                                                <Space>
                                                    <span>📝 {doc.original_filename}</span>
                                                    {getStatusTag(doc.status, doc.error_message)}
                                                </Space>
                                            }
                                            description={
                                                <div>
                                                    <div>Uploaded: {formatTimestamp(doc.upload_timestamp)}</div>
                                                    <div>Task ID: {doc.task_id}</div>
                                                    {doc.error_message && (
                                                        <div style={{ color: 'red' }}>Error: {doc.error_message}</div>
                                                    )}
                                                </div>
                                            }
                                        />
                                    </List.Item>
                                )}
                            />
                        </>
                    )}

                    {documents.completed.length > 0 && (
                        <>
                            <Typography.Text strong>
                                ✅ Completed Documents ({documents.completed.length}):
                            </Typography.Text>
                            <List
                                loading={loading}
                                dataSource={documents.completed}
                                locale={{ emptyText: "No completed documents yet" }}
                                renderItem={(doc: HandwrittenDocument) => (
                                    <List.Item key={doc.task_id} actions={[
                                        ...(doc.status === 'SUCCESS' ? [
                                            <Button 
                                                key="download" 
                                                type="primary"
                                                size="small"
                                                icon={<DownloadOutlined />}
                                                onClick={() => handleDownload(doc)}
                                            >
                                                Download LaTeX PDF
                                            </Button>
                                        ] : []),
                                        <Popconfirm
                                            key="delete"
                                            title="Delete document?"
                                            description={`Delete "${doc.original_filename}"? This action cannot be undone.`}
                                            onConfirm={() => handleDelete(doc.task_id)}
                                            okText="Yes, Delete"
                                            cancelText="Cancel"
                                        >
                                            <Button danger size="small" icon={<DeleteOutlined />}>
                                                Delete
                                            </Button>
                                        </Popconfirm>
                                    ]}>
                                        <List.Item.Meta
                                            title={
                                                <Space>
                                                    <span>📝 {doc.original_filename}</span>
                                                    {getStatusTag(doc.status, doc.error_message)}
                                                </Space>
                                            }
                                            description={
                                                <div>
                                                    <div>Uploaded: {formatTimestamp(doc.upload_timestamp)}</div>
                                                    {doc.processed_filename && (
                                                        <div>Processed: {doc.processed_filename}</div>
                                                    )}
                                                    <div>Task ID: {doc.task_id}</div>
                                                    {doc.error_message && (
                                                        <div style={{ color: 'red' }}>Error: {doc.error_message}</div>
                                                    )}
                                                </div>
                                            }
                                        />
                                    </List.Item>
                                )}
                            />
                        </>
                    )}

                    {documents.processing.length === 0 && documents.completed.length === 0 && !loading && (
                        <Typography.Text type="secondary">
                            No handwritten documents yet. Upload a PDF above to get started!
                        </Typography.Text>
                    )}
                </Space>
            </Card>
        </div>
    );
} 