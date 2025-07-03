package com.devops25.group;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import java.util.List;

public interface GroupRepository extends JpaRepository<Group, Long> {
    Optional<Group> findByName(String name);
    List<Group> findByUniversity(String university);
    List<Group> findByNameContainingIgnoreCase(String name); // For partial name search
    List<Group> findByUniversityContainingIgnoreCase(String university); // For partial university search
    List<Group> findByNameContainingIgnoreCaseOrUniversityContainingIgnoreCase(String nameQuery, String universityQuery); // For combined search
}