import js from "@eslint/js";
import globals from "globals";

export default [
  {
    ignores: ["_site/**", "node_modules/**"],
  },
  {
    files: ["assets/js/**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: {
        ...globals.browser,
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      "no-var": "off",
      "prefer-const": "off",
      "no-unused-vars": [
        "error",
        { args: "none", varsIgnorePattern: "^_", caughtErrorsIgnorePattern: "^_" },
      ],
      eqeqeq: ["error", "smart"],
      "no-throw-literal": "error",
    },
  },
];
