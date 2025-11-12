"use client";
import React from "react";
import { Box, Heading, Text, VStack, HStack } from "@chakra-ui/react";

export default function BooksPage() {
  const books = [
    { title: "The Great Gatsby", author: "F. Scott Fitzgerald" },
    { title: "1984", author: "George Orwell" },
    { title: "Pride and Prejudice", author: "Jane Austen" },
  ];

  return (
    <Box
      p={10}
      bg="white"
      color="blue.800"
      minH="100vh"
      fontFamily="Inter, sans-serif"
    >
      <VStack align="start" spacing={4}>
        {/* Header */}
        <HStack spacing={3}>
          <Text fontSize="3xl">📚</Text>
          <Heading color="blue.900">Browse Books</Heading>
        </HStack>

        {/* Subtext */}
        <Text fontSize="md" color="blue.600">
          Here you can view and search all available books in the library system.
        </Text>

        {/* Books Section */}
        <VStack spacing={3} w="100%" pt={2}>
          {books.map((book, i) => (
            <Box
              key={i}
              w="100%"
              border="1px solid"
              borderColor="blue.200"
              p={4}
              borderRadius="md"
              bg="blue.50"
              _hover={{
                bg: "blue.100",
                transform: "scale(1.01)",
                transition: "all 0.2s ease-in-out",
              }}
              shadow="sm"
            >
              <Text fontWeight="semibold" color="blue.900">
                {book.title}
              </Text>
              <Text color="blue.700" fontSize="sm">
                — {book.author}
              </Text>
            </Box>
          ))}
        </VStack>
      </VStack>
    </Box>
  );
}
