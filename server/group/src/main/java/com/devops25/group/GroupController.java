package com.devops25.group;

import com.devops25.group.dto.CreateGroupRequest;
import com.devops25.group.dto.GroupResponse;
import com.devops25.group.dto.UpdateGroupRequest;
import com.devops25.group.dto.GenaiQueryRequest;
import com.devops25.group.dto.ChatMessageRequest;
import com.devops25.group.dto.ChatMessageResponse;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Mono;

import java.io.IOException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/api/v1/groups")
public class GroupController {

    private static final Logger logger = LoggerFactory.getLogger(GroupController.class);
    private final GroupService groupService;
    private final GenaiService genaiService;
    private final JwtService jwtService;
    private final ObjectMapper objectMapper;

    @Autowired
    public GroupController(GroupService groupService, GenaiService genaiService, JwtService jwtService, ObjectMapper objectMapper) {
        this.groupService = groupService;
        this.genaiService = genaiService;
        this.jwtService = jwtService;
        this.objectMapper = objectMapper;
    }

    private String extractUsername(HttpServletRequest httpRequest) {
        String authHeader = httpRequest.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing or invalid Authorization header");
        }
        String token = authHeader.substring(7);
        try {
            return jwtService.extractUsername(token);
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid or expired token");
        }
    }

    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<GroupResponse> createGroup(
            @Valid @RequestBody CreateGroupRequest request,
            HttpServletRequest httpRequest
    ) {
        String ownerUsername = extractUsername(httpRequest);
        GroupResponse response = groupService.createGroup(request, ownerUsername);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<GroupResponse>> getAllGroups(HttpServletRequest httpRequest) {
        String authenticatedUsername = null;
        try {
            authenticatedUsername = extractUsername(httpRequest);
        } catch (ResponseStatusException e) {
            // Unauthenticated is allowed for listing all groups
        }
        List<GroupResponse> groups = groupService.getAllGroups(authenticatedUsername);
        return ResponseEntity.ok(groups);
    }

    @GetMapping("/my-groups")
    public ResponseEntity<List<GroupResponse>> getMyGroups(HttpServletRequest httpRequest) {
        String ownerUsername = extractUsername(httpRequest);
        List<GroupResponse> groups = groupService.getGroupsByOwnerUsername(ownerUsername);
        return ResponseEntity.ok(groups);
    }

    @GetMapping("/{id}")
    public ResponseEntity<GroupResponse> getGroupById(
            @PathVariable Long id,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = null;
        try {
            authenticatedUsername = extractUsername(httpRequest);
        } catch (ResponseStatusException e) {
        }
        GroupResponse group = groupService.getGroupById(id, authenticatedUsername);
        return ResponseEntity.ok(group);
    }

    @GetMapping("/search")
    public ResponseEntity<List<GroupResponse>> searchGroups(
            @RequestParam String query,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = null;
        try {
            authenticatedUsername = extractUsername(httpRequest);
        } catch (ResponseStatusException e) {
            // Unauthenticated allowed
        }
        List<GroupResponse> groups = groupService.searchGroups(query, authenticatedUsername);
        return ResponseEntity.ok(groups);
    }

    @PutMapping(value = "/{id}", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<GroupResponse> updateGroup(
            @PathVariable Long id,
            @Valid @RequestBody UpdateGroupRequest request,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = extractUsername(httpRequest);
        GroupResponse response = groupService.updateGroup(id, request, authenticatedUsername);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteGroup(
            @PathVariable Long id,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = extractUsername(httpRequest);
        groupService.deleteGroup(id, authenticatedUsername);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{id}/join")
    public ResponseEntity<GroupResponse> joinGroup(
            @PathVariable Long id,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = extractUsername(httpRequest);
        GroupResponse response = groupService.joinGroup(id, authenticatedUsername);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{id}/leave")
    public ResponseEntity<GroupResponse> leaveGroup(
            @PathVariable Long id,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = extractUsername(httpRequest);
        GroupResponse response = groupService.leaveGroup(id, authenticatedUsername);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{groupId}/documents")
    public Mono<ResponseEntity<Object>> uploadDocument(
            @PathVariable Long groupId,
            @RequestParam("file") MultipartFile file,
            HttpServletRequest httpRequest) {
        extractUsername(httpRequest);
        logger.info("Received document upload request for group ID: {}. Filename: {}, Size: {} bytes",
                groupId, file.getOriginalFilename(), file.getSize());

        if (file.isEmpty()) {
            logger.warn("Uploaded file is empty for group ID: {}", groupId);
            return Mono.just(ResponseEntity.status(HttpStatus.BAD_REQUEST).body("File cannot be empty."));
        }

        try {
            return genaiService.uploadDocument(String.valueOf(groupId), file)
                    .map(response -> {
                        try {
                            return ResponseEntity.ok(objectMapper.readTree(response));
                        } catch (JsonProcessingException e) {
                            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage());
                        }
                    })
                    .map(response -> (ResponseEntity<Object>) response)
                    .defaultIfEmpty(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build());
        } catch (IOException e) {
            logger.error("Error processing document upload for group ID: {}", groupId, e);
            return Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage()));
        }
    }

    @PostMapping("/{groupId}/chat")
    public Mono<ResponseEntity<String>> genaiChat(
            @PathVariable Long groupId,
            @Valid @RequestBody GenaiQueryRequest request,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = extractUsername(httpRequest);
        logger.info("Received chat query for group ID: {}. Question: {}", groupId, request.getQuestion());

        return genaiService.query(String.valueOf(groupId), request.getQuestion())
                .map(response -> {
                    try {
                        return ResponseEntity.ok(objectMapper.writeValueAsString(objectMapper.readTree(response)));
                    } catch (JsonProcessingException e) {
                        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage());
                    }
                })
                .defaultIfEmpty(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build());
    }

    // Group chat endpoints
    @GetMapping("/{groupId}/messages")
    public ResponseEntity<List<ChatMessageResponse>> getGroupChatMessages(
            @PathVariable Long groupId,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = extractUsername(httpRequest);
        List<ChatMessageResponse> messages = groupService.getGroupChatMessages(groupId, authenticatedUsername);
        return ResponseEntity.ok(messages);
    }

    @PostMapping("/{groupId}/messages")
    public ResponseEntity<ChatMessageResponse> sendChatMessage(
            @PathVariable Long groupId,
            @Valid @RequestBody ChatMessageRequest request,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = extractUsername(httpRequest);
        ChatMessageResponse response = groupService.sendChatMessage(groupId, request, authenticatedUsername);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{groupId}/messages")
    public ResponseEntity<Void> deleteGroupChat(
            @PathVariable Long groupId,
            HttpServletRequest httpRequest
    ) {
        String authenticatedUsername = extractUsername(httpRequest);
        groupService.deleteGroupChat(groupId, authenticatedUsername);
        return ResponseEntity.noContent().build();
    }
}
