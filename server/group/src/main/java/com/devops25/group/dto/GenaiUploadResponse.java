package com.devops25.group.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GenaiUploadResponse {
    private String filename;
    private String message;
    private String taskId;
} 