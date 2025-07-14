package com.devops25.files;

import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.core.io.PathResource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;

import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {
    private final FileService service;
    private final JwtService jwt;

    private String extractUsername(HttpServletRequest req) {
        String h = req.getHeader("Authorization");
        if (h == null || !h.startsWith("Bearer ")) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing token");
        }
        return jwt.extractUsername(h.substring(7));
    }

    @GetMapping("/{groupId}")
    public List<FileResponse> list(@PathVariable Long groupId,
                                   HttpServletRequest req) {
        extractUsername(req); // must be logged in
        return service.listFiles(groupId).stream()
                .map(FileResponse::from)
                .collect(Collectors.toList());
    }

    @PostMapping("/{groupId}/upload")
    public FileResponse upload(@PathVariable Long groupId,
                               @RequestParam("file") MultipartFile file,
                               HttpServletRequest req) {
        String user = extractUsername(req);
        return FileResponse.from(service.store(groupId, user, file));
    }

    @GetMapping("/download/{fileId}")
    public ResponseEntity<Resource> download(@PathVariable Long fileId,
                                             HttpServletRequest req) {
        extractUsername(req);
        FileEntity meta = service.getMetadata(fileId);
        Path p = Path.of(meta.getStoragePath());
        Resource r = new PathResource(p);
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + meta.getFileName() + "\"")
                .body(r);
    }

    @DeleteMapping("/{fileId}")
    public ResponseEntity<Void> delete(@PathVariable Long fileId,
                                       HttpServletRequest req) {
        String user = extractUsername(req);
        service.delete(fileId, user);
        return ResponseEntity.noContent().build();
    }
}
