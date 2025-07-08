package com.devops25.group.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class CreateGroupRequest {
    @NotBlank(message = "Group name is required")
    @Size(max = 50, message = "Group name cannot exceed 50 characters")
    private String name;

    @NotBlank(message = "University is required")
    @Size(max = 50, message = "University name cannot exceed 50 characters")
    private String university;

    @Size(max = 300, message = "Description cannot exceed 300 characters")
    private String description;

    // This might be an initial placeholder for a default image URL or a path
    // For actual file uploads, you'd handle this differently (e.g., multipart file in controller)
    private String imageUrl;
}