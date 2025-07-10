import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../auth/AuthProvider';
import { Button, List, Upload, message, Typography } from 'antd';
import type { RcFile, UploadProps } from 'antd/es/upload';

interface FileMeta {
    id: number;
    fileName: string;
    uploaderUsername: string;
    uploadedAt: string;
}

export function Material() {
    const { groupId } = useParams<{ groupId: string }>();
    const auth = useAuth();

    const [files, setFiles] = useState<FileMeta[]>([]);
    const [loading, setLoading] = useState<boolean>(false);

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

    useEffect(() => {
        fetchFiles();
    }, [groupId]);

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

    return (
        <div style={{ padding: 16 }}>
            <Typography.Title level={4}>Materials</Typography.Title>
            <Upload {...uploadProps}>
                <Button type="primary" disabled={!auth.token}>
                    Upload a file
                </Button>
            </Upload>
            <List
                style={{ marginTop: 16 }}
                loading={loading}
                dataSource={files}
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
        </div>
    );
}