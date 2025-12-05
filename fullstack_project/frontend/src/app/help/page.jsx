"use client";

import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Stack,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react";

const HelpPage = () => {
  return (
    <Container maxW="6xl" py={10}>
      <Stack spacing={6}>
        <Box>
          <Heading size="lg">Help &amp; Support</Heading>
          <Text color="gray.500">
            Start a conversation with our team. Messaging is coming soon, but
            you can hop into the chat space from anywhere.
          </Text>
        </Box>

        <Flex gap={6} direction={{ base: "column", lg: "row" }}>
          <VStack
            align="stretch"
            flex={2}
            spacing={4}
            borderWidth="1px"
            borderRadius="lg"
            p={4}
            bg="chakra-body-bg"
          >
            <Text fontWeight="bold">Message thread</Text>
            <VStack align="stretch" spacing={3}>
              <Box
                alignSelf="flex-start"
                bg="gray.100"
                _dark={{ bg: "gray.800" }}
                borderRadius="md"
                p={3}
              >
                <Text fontWeight="semibold">Support</Text>
                <Text fontSize="sm">Hey there! How can we help today?</Text>
              </Box>
              <Box
                alignSelf="flex-end"
                bg="blue.500"
                color="white"
                borderRadius="md"
                p={3}
              >
                <Text fontWeight="semibold">You</Text>
                <Text fontSize="sm">Just exploring the new help chat.</Text>
              </Box>
              <Box
                alignSelf="flex-start"
                bg="gray.100"
                _dark={{ bg: "gray.800" }}
                borderRadius="md"
                p={3}
              >
                <Text fontWeight="semibold">Support</Text>
                <Text fontSize="sm">
                  We&apos;re online and ready when you are.
                </Text>
              </Box>
            </VStack>
          </VStack>

          <VStack
            align="stretch"
            flex={1}
            spacing={4}
            borderWidth="1px"
            borderRadius="lg"
            p={4}
            bg="chakra-body-bg"
          >
            <Text fontWeight="bold">Start a new chat</Text>
            <Textarea
              placeholder="Describe what you need help with..."
              minH="120px"
            />
            <Button colorPalette="blue" disabled>
              Send (coming soon)
            </Button>
            <Text fontSize="sm" color="gray.500">
              Sending is disabled while we wire up messaging. You can still
              return here anytime from the help icon next to your profile.
            </Text>
          </VStack>
        </Flex>
      </Stack>
    </Container>
  );
};

export default HelpPage;
