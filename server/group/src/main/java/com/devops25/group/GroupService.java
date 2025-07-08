package com.devops25.group;

import com.devops25.group.dto.CreateGroupRequest;
import com.devops25.group.dto.GroupResponse;
import com.devops25.group.dto.UpdateGroupRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional; // Import Transactional
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

    @Transactional
    public GroupResponse createGroup(CreateGroupRequest request, String ownerUsername) {
        if (groupRepository.findByName(request.getName()).isPresent()) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Group with name " + request.getName() + " already exists.");
        }

        Group newGroup = Group.builder()
                .name(request.getName())
                .description(request.getDescription())
                .university(request.getUniversity())
                .imageUrl(request.getImageUrl())
                .filesServiceUrl(null)
                .ownerUsername(ownerUsername)
                .build();
        newGroup.getMemberUsernames().add(ownerUsername); // Owner is automatically a member

        Group savedGroup = groupRepository.save(newGroup);
        return mapToGroupResponse(savedGroup, ownerUsername); // Pass ownerUsername for isMember check
    }

    public List<GroupResponse> getAllGroups(String authenticatedUsername) {
        return groupRepository.findAll().stream()
                .map(group -> mapToGroupResponse(group, authenticatedUsername))
                .collect(Collectors.toList());
    }

    public List<GroupResponse> getGroupsByOwnerUsername(String ownerUsername) {
        return groupRepository.findByOwnerUsername(ownerUsername).stream()
                .map(group -> mapToGroupResponse(group, ownerUsername)) // Owner is always a member
                .collect(Collectors.toList());
    }

    public GroupResponse getGroupById(Long id, String authenticatedUsername) {
        Group group = groupRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Group not found with ID: " + id));
        return mapToGroupResponse(group, authenticatedUsername);
    }

    public List<GroupResponse> searchGroups(String query, String authenticatedUsername) {
        if (query == null || query.trim().isEmpty()) {
            return getAllGroups(authenticatedUsername);
        }
        String lowerCaseQuery = query.toLowerCase();
        return groupRepository.findByNameContainingIgnoreCaseOrUniversityContainingIgnoreCase(lowerCaseQuery, lowerCaseQuery).stream()
                .map(group -> mapToGroupResponse(group, authenticatedUsername))
                .collect(Collectors.toList());
    }

    @Transactional
    public GroupResponse updateGroup(Long id, UpdateGroupRequest request, String authenticatedUsername) {
        Group existingGroup = groupRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Group not found with ID: " + id));

        if (!existingGroup.getOwnerUsername().equals(authenticatedUsername)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "You do not have permission to update this group.");
        }

        Optional.ofNullable(request.getName()).ifPresent(existingGroup::setName);
        Optional.ofNullable(request.getDescription()).ifPresent(existingGroup::setDescription);
        Optional.ofNullable(request.getUniversity()).ifPresent(existingGroup::setUniversity);
        Optional.ofNullable(request.getImageUrl()).ifPresent(existingGroup::setImageUrl);

        Group updatedGroup = groupRepository.save(existingGroup);
        return mapToGroupResponse(updatedGroup, authenticatedUsername);
    }

    @Transactional
    public void deleteGroup(Long id, String authenticatedUsername) {
        Group existingGroup = groupRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Group not found with ID: " + id));

        // ⭐ ADD THIS LOG LINE ⭐
        System.out.println("Attempting to delete group ID: " + id +
                ". Group Owner: '" + existingGroup.getOwnerUsername() +
                "', Authenticated User: '" + authenticatedUsername + "'");

        if (!existingGroup.getOwnerUsername().equals(authenticatedUsername)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "You do not have permission to delete this group.");
        }
        groupRepository.deleteById(id);
    }

    @Transactional
    public GroupResponse joinGroup(Long groupId, String usernameToJoin) {
        Group group = groupRepository.findById(groupId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Group not found with ID: " + groupId));

        if (group.getOwnerUsername().equals(usernameToJoin)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Owner cannot join their own group (already a member)");
        }

        if (group.getMemberUsernames().contains(usernameToJoin)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "User is already a member of this group.");
        }

        group.getMemberUsernames().add(usernameToJoin);
        Group updatedGroup = groupRepository.save(group);
        return mapToGroupResponse(updatedGroup, usernameToJoin);
    }

    // NEW: Leave Group
    @Transactional
    public GroupResponse leaveGroup(Long groupId, String usernameToLeave) {
        Group group = groupRepository.findById(groupId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Group not found with ID: " + groupId));

        if (group.getOwnerUsername().equals(usernameToLeave)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Owner cannot leave their own group.");
        }

        if (!group.getMemberUsernames().contains(usernameToLeave)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "User is not a member of this group.");
        }

        group.getMemberUsernames().remove(usernameToLeave);
        Group updatedGroup = groupRepository.save(group);
        return mapToGroupResponse(updatedGroup, usernameToLeave);
    }

    // Modified mapToGroupResponse to include isMember check
    private GroupResponse mapToGroupResponse(Group group, String authenticatedUsername) {
        boolean isMember = authenticatedUsername != null && group.getMemberUsernames().contains(authenticatedUsername);

        return GroupResponse.builder()
                .id(group.getId())
                .name(group.getName())
                .description(group.getDescription())
                .university(group.getUniversity())
                .imageUrl(group.getImageUrl())
                .filesServiceUrl(group.getFilesServiceUrl())
                .ownerUsername(group.getOwnerUsername())
                .memberUsernames(group.getMemberUsernames()) // Include all member usernames
                .isMember(isMember) // Indicate if the current authenticated user is a member
                .build();
    }
}