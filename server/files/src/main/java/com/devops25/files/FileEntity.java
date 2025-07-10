package com.devops25.files;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;

@Entity
@Table(name = "files")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class FileEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // original filename
    @Column(nullable = false)
    private String fileName;

    // where on disk we stored it
    @Column(nullable = false)
    private String storagePath;

    // who uploaded it
    @Column(nullable = false)
    private String uploaderUsername;

    // which group it belongs to
    @Column(nullable = false)
    private Long groupId;

    // upload timestamp
    @Column(nullable = false)
    private Instant uploadedAt;
}
