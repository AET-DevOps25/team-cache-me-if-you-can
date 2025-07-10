package com.devops25.group.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Set;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class GroupResponse {
    private Long id;
    private String name;
    private String description;
    private String university;
    private String imageUrl; // This will likely be a URL to the image in your files service
    private String filesServiceUrl; // The URL/ID pointing to group-specific files
    private String ownerUsername;
    private Set<String> memberUsernames;

    private boolean isMember;
}