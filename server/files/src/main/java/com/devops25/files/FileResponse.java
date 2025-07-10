package com.devops25.files;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

import java.time.Instant;

@Data @Builder @AllArgsConstructor
public class FileResponse {
    private Long id;
    private String fileName;
    private String uploaderUsername;
    private Instant uploadedAt;

    static FileResponse from(FileEntity e) {
        return FileResponse.builder()
                .id(e.getId())
                .fileName(e.getFileName())
                .uploaderUsername(e.getUploaderUsername())
                .uploadedAt(e.getUploadedAt())
                .build();
    }
}
