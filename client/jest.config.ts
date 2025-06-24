import type { Config } from "jest";
import "text-encoding";

const config: Config = {
  rootDir: "./",
  testEnvironment: "jest-environment-jsdom",
  setupFilesAfterEnv: ["<rootDir>/test/jest.setup.ts"],
  transform: {
    "^.+\\.tsx?$": "ts-jest",
  },
  moduleNameMapper: {
    "\\.(gif|ttf|eot|svg|png)$": "<rootDir>/test/mocks/fileMock.js",
    "\\.(css|less|scss|sass)$": "<rootDir>/test/mocks/styleMock.js",
  },
};

export default config;
