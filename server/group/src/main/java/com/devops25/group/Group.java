package com.devops25.group;

import jakarta.persistence.*;
import lombok.*;

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
}