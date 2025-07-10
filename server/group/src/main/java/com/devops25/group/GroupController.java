package com.devops25.group;

import com.devops25.group.dto.CreateGroupRequest;
import com.devops25.group.dto.GroupResponse;
import com.devops25.group.dto.UpdateGroupRequest;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@RestController
@RequestMapping("/api/v1/groups")
public class GroupController {

    private final GroupService groupService;
    private final JwtService jwtService;

    @Autowired
    public GroupController(GroupService groupService, JwtService jwtService) {
        this.groupService = groupService;
        this.jwtService = jwtService;
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
}
