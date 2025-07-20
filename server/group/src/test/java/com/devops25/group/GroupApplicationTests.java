package com.devops25.group;

import com.devops25.group.dto.CreateGroupRequest;
import com.devops25.group.dto.GroupResponse;
import com.devops25.group.dto.ChatMessageRequest;
import com.devops25.group.dto.ChatMessageResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.context.TestConfiguration;            // <-- correct import
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.Set;

import static org.hamcrest.Matchers.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = GroupController.class)
@AutoConfigureMockMvc(addFilters = false)
@Import(GroupControllerTests.TestConfig.class)
class GroupControllerTests {

	@Autowired MockMvc mockMvc;
	@Autowired ObjectMapper objectMapper;
	@Autowired GroupService groupService;
	@Autowired GenaiService genaiService;
	@Autowired JwtService jwtService;

	@TestConfiguration
	static class TestConfig {
		@Bean GroupService groupService()         { return Mockito.mock(GroupService.class); }
		@Bean GenaiService genaiService()         { return Mockito.mock(GenaiService.class); }
		@Bean JwtService jwtService()             { return Mockito.mock(JwtService.class); }
		@Bean ObjectMapper objectMapper() {
			ObjectMapper m = new ObjectMapper();
			m.registerModule(new JavaTimeModule());
			m.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
			return m;
		}
	}

	@Test
	void createGroup_ReturnsCreated_WhenValidRequest() throws Exception {
		String user = "testuser";
		CreateGroupRequest req = CreateGroupRequest.builder()
				.name("Test Group").university("Test Uni")
				.description("A test group").imageUrl("http://example.com/img.jpg")
				.build();
		GroupResponse resp = GroupResponse.builder()
				.id(1L).name("Test Group").university("Test Uni")
				.description("A test group").imageUrl("http://example.com/img.jpg")
				.ownerUsername(user).memberUsernames(Set.of(user)).isMember(true).build();

		when(jwtService.extractUsername("valid-token")).thenReturn(user);
		when(groupService.createGroup(any(), eq(user))).thenReturn(resp);

		mockMvc.perform(post("/api/v1/groups")
						.header("Authorization", "Bearer valid-token")
						.contentType(MediaType.APPLICATION_JSON)
						.content(objectMapper.writeValueAsString(req)))
				.andExpect(status().isCreated())
				.andExpect(jsonPath("$.ownerUsername").value(user))
				.andExpect(jsonPath("$.memberUsernames", hasSize(1)))
				.andExpect(jsonPath("$.member").value(true));
	}

	@Test
	void getGroupById_ReturnsOk_WhenGroupExists() throws Exception {
		String user = "testuser";
		GroupResponse resp = GroupResponse.builder()
				.id(1L).name("Test Group").university("Test Uni")
				.description("A test group")
				.ownerUsername("owner").memberUsernames(Set.of("owner", user))
				.isMember(true).build();

		when(jwtService.extractUsername("valid-token")).thenReturn(user);
		when(groupService.getGroupById(1L, user)).thenReturn(resp);

		mockMvc.perform(get("/api/v1/groups/1")
						.header("Authorization", "Bearer valid-token"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.memberUsernames", containsInAnyOrder("owner", user)))
				.andExpect(jsonPath("$.member").value(true));
	}

	@Test
	void joinGroup_ReturnsOk_WhenUserJoins() throws Exception {
		String user = "testuser";
		GroupResponse resp = GroupResponse.builder()
				.id(1L).name("Test Group").university("Test Uni")
				.ownerUsername("owner").memberUsernames(Set.of("owner", user))
				.isMember(true).build();

		when(jwtService.extractUsername("valid-token")).thenReturn(user);
		when(groupService.joinGroup(1L, user)).thenReturn(resp);

		mockMvc.perform(post("/api/v1/groups/1/join")
						.header("Authorization", "Bearer valid-token"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.memberUsernames", hasSize(2)))
				.andExpect(jsonPath("$.memberUsernames", containsInAnyOrder("owner", user)))
				.andExpect(jsonPath("$.member").value(true));
	}

	@Test
	void sendChatMessage_ReturnsOk_WhenMessageSent() throws Exception {
		String user = "testuser";
		ChatMessageRequest req = ChatMessageRequest.builder()
				.content("Hello, group!").build();
		ChatMessageResponse resp = ChatMessageResponse.builder()
				.id(1L).username(user).content("Hello, group!")
				.timestamp(LocalDateTime.now()).build();

		when(jwtService.extractUsername("valid-token")).thenReturn(user);
		when(groupService.sendChatMessage(eq(1L), any(), eq(user))).thenReturn(resp);

		mockMvc.perform(post("/api/v1/groups/1/messages")
						.header("Authorization", "Bearer valid-token")
						.contentType(MediaType.APPLICATION_JSON)
						.content(objectMapper.writeValueAsString(req)))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.username").value(user))
				.andExpect(jsonPath("$.timestamp").exists());
	}
}
