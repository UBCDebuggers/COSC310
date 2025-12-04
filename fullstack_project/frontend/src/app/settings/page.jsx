"use client";

import React, { useEffect, useState } from "react";
import { Box, Button, Container, Field, Heading, Stack, Text, VStack } from "@chakra-ui/react";
import { useColorMode } from "@/components/ui/color-mode";

const SettingsPage = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  const [language, setLanguage] = useState("en");
  const [emailNotifications, setEmailNotifications] = useState(false);
  const [success, setSuccess] = useState(null);
  const [emailStatus, setEmailStatus] = useState("");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const savedLang = localStorage.getItem("settings_language");
    const savedEmail = localStorage.getItem("settings_email_notifications");
    if (savedLang) setLanguage(savedLang);
    if (savedEmail) {
      const isOn = savedEmail === "true";
      setEmailNotifications(isOn);
      setEmailStatus(isOn ? "Email updates: ON (demo)" : "Email updates: OFF (demo)");
    }
  }, []);

  const handleSave = () => {
    if (typeof window === "undefined") return;
    localStorage.setItem("settings_language", language);
    localStorage.setItem("settings_email_notifications", String(emailNotifications));
    setEmailStatus(emailNotifications ? "Email updates: ON (demo)" : "Email updates: OFF (demo)");
    setSuccess("Settings saved (stored locally for demo).");
  };

  const handleThemeToggle = () => {
    toggleColorMode();
    setSuccess(`Theme set to ${colorMode === "dark" ? "light" : "dark"}.`);
  };

  return (
    <Container maxW="3xl" py={10}>
      <VStack align="stretch" spacing={6}>
        <Box>
          <Heading size="lg">Settings</Heading>
          <Text color="gray.500">Adjust your preferences.</Text>
        </Box>

        {success && (
          <Box borderWidth="1px" borderColor="green.500" borderRadius="md" p={3} color="green.600">
            {success}
          </Box>
        )}

        <Box borderWidth="1px" borderRadius="md" p={6} bg="chakra-body-bg">
          <VStack spacing={4} align="stretch">
            <Heading size="md">Appearance</Heading>
            <Text color="gray.500">Current theme: {colorMode}</Text>
            <Button onClick={handleThemeToggle}>Toggle Theme</Button>
          </VStack>
        </Box>

        <Box borderWidth="1px" borderRadius="md" p={6} bg="chakra-body-bg">
          <VStack spacing={4} align="stretch">
            <Heading size="md">Preferences</Heading>

            <Field.Root>
              <Field.Label>Language</Field.Label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ padding: "10px", borderRadius: "6px", border: "1px solid #444" }}
              >
                <option value="en">English</option>
                <option value="fr">French</option>
              </select>
            </Field.Root>

            <Field.Root>
              <Field.Label>Email Notifications</Field.Label>
              <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <input
                  type="checkbox"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                />
                <Text>Receive email updates</Text>
              </label>
              {emailStatus && (
                <Text color="gray.500" fontSize="sm" mt={1}>
                  {emailStatus}
                </Text>
              )}
            </Field.Root>

            <Stack direction={{ base: "column", sm: "row" }} spacing={4} pt={2}>
              <Button onClick={handleSave} flex={1}>
                Save Preferences
              </Button>
              <Button variant="outline" onClick={() => setSuccess(null)} flex={1}>
                Clear Message
              </Button>
            </Stack>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default SettingsPage;
