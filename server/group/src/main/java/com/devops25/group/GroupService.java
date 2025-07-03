package com.devops25.group;

import com.devops25.group.Group;
import com.devops25.group.GroupRepository;
import com.devops25.group.dto.CreateGroupRequest;
import com.devops25.group.dto.GroupResponse;
import com.devops25.group.dto.UpdateGroupRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class GroupService {

    private final GroupRepository groupRepository;

    @Autowired
    public GroupService(GroupRepository groupRepository) {
        this.groupRepository = groupRepository;
    }

    public GroupResponse createGroup(CreateGroupRequest request) {
        // Check if group with same name already exists
        if (groupRepository.findByName(request.getName()).isPresent()) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Group with name " + request.getName() + " already exists.");
        }

        Group newGroup = Group.builder()
                .name(request.getName())
                .description(request.getDescription())
                .university(request.getUniversity())
                .imageUrl(request.getImageUrl()) // Store the provided image URL
                // TODO: Integrate with files service to get actual filesServiceUrl/ID for group documents
                .filesServiceUrl(null) // Placeholder for now
                .build();

        Group savedGroup = groupRepository.save(newGroup);
        return mapToGroupResponse(savedGroup);
    }

    public List<GroupResponse> getAllGroups() {
        return groupRepository.findAll().stream()
                .map(this::mapToGroupResponse)
                .collect(Collectors.toList());
    }

    public GroupResponse getGroupById(Long id) {
        Group group = groupRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Group not found with ID: " + id));
        return mapToGroupResponse(group);
    }

    public List<GroupResponse> searchGroups(String query) {
        if (query == null || query.trim().isEmpty()) {
            return getAllGroups(); // Or return an empty list or throw an error depending on desired behavior
        }
        String lowerCaseQuery = query.toLowerCase();
        return groupRepository.findByNameContainingIgnoreCaseOrUniversityContainingIgnoreCase(lowerCaseQuery, lowerCaseQuery).stream()
                .map(this::mapToGroupResponse)
                .collect(Collectors.toList());
    }

    public GroupResponse updateGroup(Long id, UpdateGroupRequest request) {
        Group existingGroup = groupRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Group not found with ID: " + id));

        // Update fields if provided in the request
        Optional.ofNullable(request.getName()).ifPresent(existingGroup::setName);
        Optional.ofNullable(request.getDescription()).ifPresent(existingGroup::setDescription);
        Optional.ofNullable(request.getUniversity()).ifPresent(existingGroup::setUniversity);
        Optional.ofNullable(request.getImageUrl()).ifPresent(existingGroup::setImageUrl); // Update image URL

        Group updatedGroup = groupRepository.save(existingGroup);
        return mapToGroupResponse(updatedGroup);
    }

    public void deleteGroup(Long id) {
        if (!groupRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Group not found with ID: " + id);
        }
        groupRepository.deleteById(id);
    }

    private GroupResponse mapToGroupResponse(Group group) {
        return GroupResponse.builder()
                .id(group.getId())
                .name(group.getName())
                .description(group.getDescription())
                .university(group.getUniversity())
                .imageUrl(group.getImageUrl()) // Use imageUrl
                .filesServiceUrl(group.getFilesServiceUrl())
                .build();
    }
}