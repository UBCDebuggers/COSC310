"use client";
import React, { useEffect, useState, useContext } from "react";
import { useRouter } from "next/navigation";
import AuthContext from "../context/AuthContext";
import axios from "axios";
import {
  VStack,
  HStack,
  Text,
  Image,
  Box,
  Spinner,
  Skeleton,
} from "@chakra-ui/react";

export default function WatchlistPage() {
  const router = useRouter();
  const { user } = useContext(AuthContext);

  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.access_token) return;

    const fetchWatchlist = async () => {
      try {
        const res = await axios.get("http://localhost:8000/watchlist", {
          headers: { Authorization: `Bearer ${user.access_token}` },
        });
        setBooks(res.data);
      } catch (err) {
        console.error("Error fetching watchlist:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchWatchlist();
  }, [user]);

  const onBookClick = (isbn) => {
    router.push(`/book/${isbn}`);
  };

  if (loading) {
    return (
      <VStack w="100%" p={5}>
        <Spinner size="xl" />
      </VStack>
    );
  }

  return (
    <VStack w="100%" alignItems="flex-start" p={5} gap={4}>
      {books.map((book) => (
        <HStack
          key={book.isbn}
          w="100%"
          p={3}
          borderRadius="lg"
          borderWidth="1px"
          cursor="pointer"
          _hover={{ bg: "gray.100" }}
          onClick={() => onBookClick(book.isbn)}
        >
          <Image
            src={book.img_url_m || "/no-image.png"}
            alt={book.title}
            boxSize="80px"
            objectFit="cover"
            fallbackSrc="/no-image.png"
          />

          <VStack align="flex-start" spacing={0}>
            <Text fontWeight="bold" fontSize="lg">
              {book.title}
            </Text>
            <Text fontSize="sm" color="gray.600">
              {book.author}
            </Text>
            <Text fontSize="xs" color="gray.500">
              {book.publisher}
            </Text>
          </VStack>
        </HStack>
      ))}
    </VStack>
  );
}
