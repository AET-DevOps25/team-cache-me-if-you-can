package com.devops25.files;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class FileControllerTests {

	private MockMvc mockMvc;

	@Mock
	private FileService fileService;

	@Mock
	private JwtService jwtService;

	@InjectMocks
	private FileController fileController;

	private final ObjectMapper objectMapper = new ObjectMapper();

	@BeforeEach
	void setup() {
		mockMvc = MockMvcBuilders.standaloneSetup(fileController).build();
	}

	@Test
	void listFiles_ReturnsFileList_WhenAuthenticated() throws Exception {
		Long groupId = 1L;
		String username = "testuser";
		FileEntity file = FileEntity.builder()
				.id(1L)
				.fileName("test.txt")
				.uploaderUsername(username)
				.groupId(groupId)
				.storagePath("some/path")
				.uploadedAt(Instant.now())
				.build();

		when(jwtService.extractUsername(any(String.class))).thenReturn(username);
		when(fileService.listFiles(groupId)).thenReturn(List.of(file));

		mockMvc.perform(get("/api/files/" + groupId)
						.header("Authorization", "Bearer valid-token"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$[0].fileName").value("test.txt"))
				.andExpect(jsonPath("$[0].uploaderUsername").value(username));
	}

	@Test
	void uploadFile_ReturnsFileResponse_WhenValidFile() throws Exception {
		Long groupId = 1L;
		String username = "testuser";
		MockMultipartFile mockFile = new MockMultipartFile(
				"file",
				"test.txt",
				MediaType.TEXT_PLAIN_VALUE,
				"Hello, World!".getBytes()
		);
		FileEntity savedFile = FileEntity.builder()
				.id(1L)
				.fileName("test.txt")
				.uploaderUsername(username)
				.groupId(groupId)
				.storagePath("some/path")
				.uploadedAt(Instant.now())
				.build();

		when(jwtService.extractUsername(any(String.class))).thenReturn(username);
		when(fileService.store(eq(groupId), eq(username), any())).thenReturn(savedFile);

		mockMvc.perform(multipart("/api/files/" + groupId + "/upload")
						.file(mockFile)
						.header("Authorization", "Bearer valid-token"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.fileName").value("test.txt"))
				.andExpect(jsonPath("$.uploaderUsername").value(username));
	}

	@Test
	void downloadFile_ReturnsFileResource_WhenFileExists() throws Exception {
		// Create a temporary file to simulate storage
		Path tempFile = Files.createTempFile("test", ".txt");
		Files.writeString(tempFile, "sample data");
		Long fileId = 1L;
		String username = "testuser";
		FileEntity meta = FileEntity.builder()
				.id(fileId)
				.fileName(tempFile.getFileName().toString())
				.uploaderUsername(username)
				.groupId(1L)
				.storagePath(tempFile.toString())
				.uploadedAt(Instant.now())
				.build();

		when(jwtService.extractUsername(any(String.class))).thenReturn(username);
		when(fileService.getMetadata(fileId)).thenReturn(meta);

		mockMvc.perform(get("/api/files/download/" + fileId)
						.header("Authorization", "Bearer valid-token"))
				.andExpect(status().isOk())
				.andExpect(header().string("Content-Disposition", "attachment; filename=\"" + tempFile.getFileName() + "\""))
				.andExpect(content().contentType(MediaType.APPLICATION_OCTET_STREAM));
	}

	@Test
	void deleteFile_ReturnsNoContent_WhenAuthorized() throws Exception {
		Long fileId = 1L;
		String username = "testuser";
		FileEntity file = FileEntity.builder()
				.id(fileId)
				.fileName("test.txt")
				.uploaderUsername(username)
				.groupId(1L)
				.storagePath("some/path")
				.uploadedAt(Instant.now())
				.build();

		when(jwtService.extractUsername(any(String.class))).thenReturn(username);
		when(fileService.getMetadata(fileId)).thenReturn(file);
		doNothing().when(fileService).delete(eq(fileId), eq(username));

		mockMvc.perform(delete("/api/files/" + fileId)
						.header("Authorization", "Bearer valid-token"))
				.andExpect(status().isNoContent());
	}
}