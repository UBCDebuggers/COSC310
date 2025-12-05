"use client";

import React, { useEffect, useState, useContext } from "react";
import { useRouter } from "next/navigation";
import AuthContext from "../context/AuthContext";
import axios from "axios";
import { VStack, HStack, Text, Image, Spinner } from "@chakra-ui/react";

export default function HistoryPage() {
  const router = useRouter();
  const { user } = useContext(AuthContext);

  const [items, setItems] = useState([]);
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.access_token) {
      router.push("/");
      return;
    }

    const fetchHistory = async () => {
      try {
        // 1️⃣ Fetch user history
        const res = await axios.get(
          `http://localhost:8000/history/user/${user?.sub}`,
          {
            headers: { Authorization: `Bearer ${user?.access_token}` },
          }
        );

        const historyItems = res.data.items || [];
        setItems(historyItems);

        const fetchedBooks = await Promise.all(
          historyItems.map(async (entry) => {
            const bookRes = await fetch(
              `http://localhost:8000/books/${entry.isbn}`
            );
            return bookRes.ok ? await bookRes.json() : null;
          })
        );

        setBooks(fetchedBooks);
      } catch (err) {
        console.error("Error fetching user history:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [user]);

  const onBookClick = (isbn) => {
    router.push(`/book/${isbn}`);
  };

  if (loading) {
    return (
      <VStack w="100%" p={5}>
        <Text fontWeight="bold" fontSize="5xl">
          History
        </Text>
        <Spinner size="xl" />
      </VStack>
    );
  }

  return (
    <VStack w="100%" alignItems="flex-start" p={5} gap={4}>
      <Text fontWeight="bold" fontSize="5xl">
        History
      </Text>

      {items.length === 0 && (
        <Text fontSize="lg" color="gray.500">
          No history found. Start by looking at books :)
        </Text>
      )}

      {items.map((entry, index) => {
        const book = books[index] || {};

        return (
          <HStack
            key={entry.isbn}
            w="100%"
            p={3}
            borderRadius="lg"
            borderWidth="1px"
            cursor="pointer"
            _hover={{ bg: "gray.100" }}
            onClick={() => onBookClick(entry.isbn)}
          >
            <Image
              src={book.img_url_m || "/no-image.png"}
              alt={book.title}
              objectFit="cover"
              fallbackSrc="/no-image.png"
              borderRadius={5}
            />

            <VStack align="flex-start">
              <Text fontWeight="bold" fontSize="lg">
                {book.title}
              </Text>

              <Text fontSize="sm" color="gray.600">
                Author: {book.author}
              </Text>
              <Text fontSize="sm" color="gray.600">
                Publisher: {book.publisher}
              </Text>

              <Text fontSize="xs" color="gray.500">
                Borrowed on: {new Date(entry.date).toLocaleDateString()}
              </Text>
            </VStack>
          </HStack>
        );
      })}
    </VStack>
  );
}
