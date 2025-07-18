package com.devops25.group;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {
    List<ChatMessage> findByGroupIdOrderByTimestampAsc(Long groupId);
    
    @Modifying
    @Query("DELETE FROM ChatMessage c WHERE c.groupId = :groupId")
    void deleteByGroupId(@Param("groupId") Long groupId);
} 