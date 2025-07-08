package com.devops25.group.dto;

import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

// For partial updates, fields can be null
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class UpdateGroupRequest {
    @Size(max = 50, message = "Group name cannot exceed 50 characters")
    private String name;

    @Size(max = 50, message = "University name cannot exceed 50 characters")
    private String university;

    @Size(max = 300, message = "Description cannot exceed 300 characters")
    private String description;

    // New URL for the image
    private String imageUrl;
}