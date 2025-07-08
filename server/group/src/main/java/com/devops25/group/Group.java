package com.devops25.group;

import jakarta.persistence.*;
import lombok.*;

import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "study_group")
@Builder
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Group {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false)
    private String university;

    private String imageUrl;

    private String filesServiceUrl; // Placeholder for group-specific files

    @Column(nullable = false) // Owner must always be present
    private String ownerUsername;

    @Builder.Default
    @ElementCollection(fetch = FetchType.LAZY) // Use LAZY to avoid fetching all members unless needed
    @CollectionTable(name = "group_members", joinColumns = @JoinColumn(name = "group_id"))
    @Column(name = "username")
    private Set<String> memberUsernames = new HashSet<>(); // Initialize to avoid null pointer
}