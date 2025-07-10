package com.devops25.files;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
public class FileService {
    private final FileRepository repo;
    private final Path uploadRoot;

    public FileService(FileRepository repo,
                       @Value("${files.upload-dir:/uploads}") String uploadDir) {
        this.repo = repo;
        this.uploadRoot = Paths.get(uploadDir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(uploadRoot);
        } catch (IOException e) {
            throw new RuntimeException("Could not create upload directory", e);
        }
    }

    public List<FileEntity> listFiles(Long groupId) {
        return repo.findByGroupId(groupId);
    }

    public FileEntity store(Long groupId, String username, MultipartFile file) {
        String ext = Path.of(file.getOriginalFilename()).getFileName().toString();
        String storedName = UUID.randomUUID() + "-" + ext;
        Path target = uploadRoot.resolve(storedName);
        try {
            Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException ex) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to store file", ex);
        }
        FileEntity e = FileEntity.builder()
                .groupId(groupId)
                .uploaderUsername(username)
                .fileName(ext)
                .storagePath(target.toString())
                .uploadedAt(Instant.now())
                .build();
        return repo.save(e);
    }

    public Path resolvePath(Long fileId) {
        FileEntity e = repo.findById(fileId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "File not found"));
        return Paths.get(e.getStoragePath());
    }

    public FileEntity getMetadata(Long fileId) {
        return repo.findById(fileId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "File not found"));
    }

    public void delete(Long fileId, String requester) {
        FileEntity e = repo.findById(fileId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "File not found"));
        if (!e.getUploaderUsername().equals(requester)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Not owner");
        }
        // delete file on disk
        try {
            Files.deleteIfExists(Paths.get(e.getStoragePath()));
        } catch (IOException ignored) {}
        repo.deleteById(fileId);
    }
}
