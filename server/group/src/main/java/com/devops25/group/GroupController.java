package com.devops25.group;

import com.devops25.group.dto.CreateGroupRequest;
import com.devops25.group.dto.GroupResponse;
import com.devops25.group.dto.UpdateGroupRequest;
import com.devops25.group.GroupService;
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

    @Autowired
    public GroupController(GroupService groupService) {
        this.groupService = groupService;
    }

    // Handles creation of a new group (image URL comes as part of JSON)
    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<GroupResponse> createGroup(@Valid @RequestBody CreateGroupRequest request) {
        GroupResponse response = groupService.createGroup(request);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    // Retrieves all groups
    @GetMapping
    public ResponseEntity<List<GroupResponse>> getAllGroups() {
        List<GroupResponse> groups = groupService.getAllGroups();
        return ResponseEntity.ok(groups);
    }

    // Retrieves a group by its ID
    @GetMapping("/{id}")
    public ResponseEntity<GroupResponse> getGroupById(@PathVariable Long id) {
        GroupResponse group = groupService.getGroupById(id);
        return ResponseEntity.ok(group);
    }

    // Searches for groups by name or university
    @GetMapping("/search")
    public ResponseEntity<List<GroupResponse>> searchGroups(@RequestParam String query) {
        List<GroupResponse> groups = groupService.searchGroups(query);
        return ResponseEntity.ok(groups);
    }

    // Updates an existing group by ID
    // Uses PUT for full replacement or PATCH for partial update depending on semantics,
    // but RequestBody with optional fields works for PATCH-like behavior here.
    @PutMapping(value = "/{id}", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<GroupResponse> updateGroup(
            @PathVariable Long id,
            @Valid @RequestBody UpdateGroupRequest request) {
        GroupResponse response = groupService.updateGroup(id, request);
        return ResponseEntity.ok(response);
    }

    // Deletes a group by ID
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteGroup(@PathVariable Long id) {
        groupService.deleteGroup(id);
        return ResponseEntity.noContent().build();
    }
}