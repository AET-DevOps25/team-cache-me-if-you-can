import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../auth/AuthProvider';
import { Button, List, Upload, message, Typography, Card, Space, Popconfirm } from 'antd';
import type { RcFile, UploadProps } from 'antd/es/upload';
import { uploadDocumentForGenai, deleteDocumentFromGenai, listGenaiDocuments } from '../../services/genaiApi';

interface FileMeta {
    id: number;
    fileName: string;
    uploaderUsername: string;
    uploadedAt: string;
}

interface AIDocument {
    source: string;
}

export function Material() {
    const { groupId } = useParams<{ groupId: string }>();
    const auth = useAuth();

    const [files, setFiles] = useState<FileMeta[]>([]);
    const [aiDocuments, setAiDocuments] = useState<AIDocument[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [aiLoading, setAiLoading] = useState<boolean>(false);
    const [genaiUploading, setGenaiUploading] = useState<boolean>(false);

    const fetchFiles = async (): Promise<void> => {
        setLoading(true);
        try {
            const res = await fetch(`/api/files/${groupId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${auth.token}`,
                },
            } as RequestInit);
            if (!res.ok) throw new Error('Could not load files');
            const data = (await res.json()) as FileMeta[];
            setFiles(data);
        } catch (error: any) {
            message.error(error.message || 'Failed to fetch files');
        } finally {
            setLoading(false);
        }
    };

    const fetchAiDocuments = async (): Promise<void> => {
        if (!groupId || !auth.token) return;
        setAiLoading(true);
        try {
            const data = await listGenaiDocuments(groupId, auth.token);
            setAiDocuments(data);
        } catch (error: any) {
            message.error(error.message || 'Failed to fetch AI documents');
        } finally {
            setAiLoading(false);
        }
    };

    useEffect(() => {
        fetchFiles();
        fetchAiDocuments();
    }, [groupId]);

    const handleGenaiUpload = async (file: RcFile) => {
        if (!groupId || !auth.token) {
            message.error("Cannot upload file: missing group ID or auth token.");
            return;
        }
        setGenaiUploading(true);
        try {
            const response = await uploadDocumentForGenai(groupId, file, auth.token);
            message.success(`Document "${file.name}" uploaded for AI processing. Task ID: ${response.task_id}`);
            // Refresh AI documents list after successful upload
            setTimeout(() => fetchAiDocuments(), 2000); // Wait a bit for processing
        } catch (error: any) {
            message.error(error.message || "Failed to upload document for AI.");
        } finally {
            setGenaiUploading(false);
        }
    };

    const handleAiDocumentDelete = async (filename: string) => {
        if (!groupId || !auth.token) return;
        try {
            await deleteDocumentFromGenai(filename, groupId, auth.token);
            message.success(`Document "${filename}" removed from AI knowledge base`);
            fetchAiDocuments(); // Refresh the list
        } catch (error: any) {
            message.error(error.message || 'Failed to delete AI document');
        }
    };

    const handleUpload = async (file: RcFile): Promise<void> => {
        const formData = new FormData();
        formData.append('file', file);
        try {
            const res = await fetch(`/api/files/${groupId}/upload`, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${auth.token}`,
                },
                body: formData,
            } as RequestInit);
            if (!res.ok) throw new Error('Upload failed');
            message.success('Uploaded!');
            fetchFiles();
        } catch (error: any) {
            message.error(error.message || 'Upload error');
        }
    };

    const handleDownload = async (id: number, name: string): Promise<void> => {
        try {
            const res = await fetch(`/api/files/download/${id}`, {
                method: 'GET',
                headers: {
                    Authorization: `Bearer ${auth.token}`,
                },
            } as RequestInit);
            if (!res.ok) throw new Error('Download failed');
            const blob = await res.blob();
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = name;
            link.click();
            URL.revokeObjectURL(link.href);
        } catch (error: any) {
            message.error(error.message || 'Download error');
        }
    };

    const handleDelete = async (id: number): Promise<void> => {
        try {
            const res = await fetch(`/api/files/${id}`, {
                method: 'DELETE',
                headers: {
                    Authorization: `Bearer ${auth.token}`,
                },
            } as RequestInit);
            if (!res.ok) throw new Error('Delete failed');
            message.success('Deleted');
            fetchFiles();
        } catch (error: any) {
            message.error(error.message || 'Delete error');
        }
    };

    const uploadProps: UploadProps = {
        beforeUpload: (file) => {
            handleUpload(file as RcFile);
            return false;
        },
        showUploadList: false,
    };

    const genaiUploadProps: UploadProps = {
        beforeUpload: (file) => {
            handleGenaiUpload(file as RcFile);
            return false;
        },
        showUploadList: false,
        disabled: genaiUploading,
    };

    return (
        <div style={{ padding: 16 }}>
            <Card style={{ marginBottom: 24 }}>
                <Typography.Title level={4}>🤖 AI Assistant Documents</Typography.Title>
                <Typography.Paragraph>
                    Upload documents (PDF, DOCX, PPTX) here to make them available for the AI Bot to answer questions about.
                </Typography.Paragraph>
                
                <Space direction="vertical" style={{ width: '100%' }}>
                    <Upload {...genaiUploadProps}>
                        <Button type="primary" size="large" loading={genaiUploading} disabled={!auth.token}>
                            📤 Upload Document for AI Assistant
                        </Button>
                    </Upload>

                    <Typography.Text strong>AI Knowledge Base ({aiDocuments.length} documents):</Typography.Text>
                    <List
                        loading={aiLoading}
                        dataSource={aiDocuments}
                        locale={{ emptyText: "No documents uploaded to AI yet. Upload some files above!" }}
                        renderItem={(doc: AIDocument) => (
                            <List.Item key={doc.source} actions={[
                                <Popconfirm
                                    key="delete"
                                    title="Remove from AI?"
                                    description={`Remove "${doc.source}" from AI knowledge base?`}
                                    onConfirm={() => handleAiDocumentDelete(doc.source)}
                                    okText="Yes, Remove"
                                    cancelText="Cancel"
                                >
                                    <Button danger size="small">
                                        🗑️ Remove from AI
                                    </Button>
                                </Popconfirm>
                            ]}>
                                <List.Item.Meta
                                    title={<span>🤖 {doc.source}</span>}
                                    description="Available for AI chat questions"
                                />
                            </List.Item>
                        )}
                    />
                </Space>
            </Card>

            <Card>
                <Typography.Title level={4}>📁 Shared Group Files</Typography.Title>
                <Typography.Paragraph>
                    Upload files to share with group members. These files are stored but not processed by AI.
                </Typography.Paragraph>
                
                <Upload {...uploadProps}>
                    <Button disabled={!auth.token}>
                        📎 Upload Shared File
                    </Button>
                </Upload>
                
                <List
                    style={{ marginTop: 16 }}
                    loading={loading}
                    dataSource={files}
                    locale={{ emptyText: "No shared files yet. Upload some files above!" }}
                    renderItem={(file: FileMeta) => (
                        <List.Item key={file.id} actions={[
                            <Button key="download" onClick={() => handleDownload(file.id, file.fileName)}>
                                Download
                            </Button>,
                            auth.user === file.uploaderUsername && (
                                <Button key="delete" danger onClick={() => handleDelete(file.id)}>
                                    Delete
                                </Button>
                            ),
                        ]}>
                            <List.Item.Meta
                                title={file.fileName}
                                description={`By ${file.uploaderUsername} on ${new Date(file.uploadedAt).toLocaleString()}`}
                            />
                        </List.Item>
                    )}
                />
            </Card>
        </div>
    );
}