"use client";
import React, { use, useEffect } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Carousel,
  HStack,
  IconButton,
  Box,
  Text,
  VStack,
  Flex,
  ScrollArea,
  Skeleton,
} from "@chakra-ui/react";
import {
  LuChevronLeft,
  LuChevronRight,
  LuMouse,
  LuMoveHorizontal,
} from "react-icons/lu";
import { set } from "react-hook-form";

const items = Array.from({ length: 5 });

const page = () => {
  const router = useRouter();
  const [topPicks, setTopPicks] = useState([]);
  const [popularBooks, setPopularBooks] = useState([]);
  const [engagingBooks, setEngagingBooks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTopPicks = async () => {
      setLoading(true);
      const [items, popularItems, engagingItems] = await Promise.all([
        fetch("http://localhost:8000/recommend/toprated/5").then((r) =>
          r.json()
        ),
        fetch("http://localhost:8000/recommend/popular/10").then((r) =>
          r.json()
        ),
        fetch("http://localhost:8000/recommend/topengagement/10").then((r) =>
          r.json()
        ),
      ]);

      const [booksTop, booksPopular, booksEngaging] = await Promise.all([
        Promise.all(
          items.map((item) =>
            fetch(
              `http://localhost:8000/books/${encodeURIComponent(item.isbn)}`
            ).then((res) => res.json())
          )
        ),

        Promise.all(
          popularItems.map((item) =>
            fetch(
              `http://localhost:8000/books/${encodeURIComponent(item.isbn)}`
            ).then((res) => res.json())
          )
        ),

        Promise.all(
          engagingItems.map((item) =>
            fetch(
              `http://localhost:8000/books/${encodeURIComponent(item.isbn)}`
            ).then((res) => res.json())
          )
        ),
      ]);

      setTopPicks(booksTop);
      setPopularBooks(booksPopular);
      setEngagingBooks(booksEngaging);
      setLoading(false);
    };

    fetchTopPicks();
  }, []);

  const handleBookClick = (isbn) => {
    router.push(`/book/${isbn}`);
  };

  return (
    <VStack w="100vw" alignItems={"flex-start"} p={10}>
      <Text fontWeight={"bold"} fontSize={30}>
        Hall of Fame
      </Text>
      <Flex
        backdropFilter="blur(5px)"
        bg={{ _dark: "gray.800", _light: "gray.300" }}
        px={10}
        py={5}
        borderRadius={10}
      >
        <Skeleton
          asChild
          loading={loading}
          variant={"shine"}
          w="40rem"
          h="20rem"
        >
          <Carousel.Root
            autoplay={true}
            slideCount={topPicks.length}
            maxW="xl"
            mx="auto"
            allowMouseDrag
          >
            <Carousel.ItemGroup>
              {topPicks.map((book, index) => (
                <Carousel.Item
                  key={index}
                  index={index}
                  onClick={() => handleBookClick(book.isbn)}
                >
                  <Flex
                    w="100%"
                    h="20rem"
                    rounded="lg"
                    fontSize="2.5rem"
                    gap={2}
                  >
                    <img
                      src={book.img_url_l}
                      style={{ borderRadius: 6, cursor: "pointer" }}
                    />
                    <Flex gap={3}>
                      <Text
                        fontSize={160}
                        mt={4}
                        fontFamily={"Times New Roman"}
                      >
                        {index + 1}
                      </Text>
                      <VStack alignItems={"center"}>
                        <Text
                          fontWeight={"bold"}
                          fontSize={20}
                          mt={4}
                          cursor={"pointer"}
                          _hover={{ textDecoration: "underline" }}
                        >
                          {book.title}
                        </Text>
                        <Text fontSize={16} color="gray.500">
                          by {book.author}
                        </Text>
                      </VStack>
                    </Flex>
                  </Flex>
                </Carousel.Item>
              ))}
            </Carousel.ItemGroup>

            <Carousel.Control justifyContent="center" gap="4">
              <Carousel.PrevTrigger asChild>
                <IconButton size="xs" variant="ghost">
                  <LuChevronLeft />
                </IconButton>
              </Carousel.PrevTrigger>

              <Carousel.Indicators borderRadius={5} />

              <Carousel.NextTrigger asChild>
                <IconButton size="xs" variant="ghost">
                  <LuChevronRight />
                </IconButton>
              </Carousel.NextTrigger>
            </Carousel.Control>
          </Carousel.Root>
        </Skeleton>
      </Flex>

      <Text fontWeight={"bold"} fontSize={30} mt={10}>
        Popular Books
      </Text>
      <ScrollArea.Root
        height="20rem"
        backdropFilter="blur(5px)"
        bg={{ _dark: "gray.800", _light: "gray.300" }}
        px={10}
        py={5}
        borderRadius={10}
        w="full"
      >
        <ScrollArea.Viewport
          css={{
            "--scroll-shadow-size": "15rem",
            maskImage:
              "linear-gradient(90deg,transparent,#000 var(--scroll-shadow-size),#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            "&[data-at-left]": {
              maskImage:
                "linear-gradient(90deg,#000,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
            "&[data-at-right]": {
              maskImage:
                "linear-gradient(90deg,transparent,#000 var(--scroll-shadow-size),#000)",
            },
          }}
        >
          <ScrollArea.Content spaceY="4">
            <Flex gap="4" flexWrap="nowrap">
              {!loading
                ? popularBooks.map((item, index) => (
                    <Box
                      width={"200px"}
                      height={"full"}
                      key={index}
                      cursor={"pointer"}
                      onClick={() => handleBookClick(item.isbn)}
                    >
                      <img
                        src={item.img_url_l}
                        key={index}
                        style={{ borderRadius: 6 }}
                      />
                    </Box>
                  ))
                : Array.from({ length: 10 }, (_, i) => (
                    <Skeleton key={i} variant={"shine"} loading={true} asChild>
                      <Box key={i} h="20rem" width={"200px"}>
                        Item {i + 1}
                      </Box>
                    </Skeleton>
                  ))}
            </Flex>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
      </ScrollArea.Root>

      <Text fontWeight={"bold"} fontSize={30} mt={10}>
        Most Engaging Reads
      </Text>
      <ScrollArea.Root
        height="20rem"
        backdropFilter="blur(5px)"
        bg={{ _dark: "gray.800", _light: "gray.300" }}
        px={10}
        py={5}
        borderRadius={10}
        w="full"
      >
        <ScrollArea.Viewport
          css={{
            "--scroll-shadow-size": "15rem",
            maskImage:
              "linear-gradient(90deg,transparent,#000 var(--scroll-shadow-size),#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            "&[data-at-left]": {
              maskImage:
                "linear-gradient(90deg,#000,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
            "&[data-at-right]": {
              maskImage:
                "linear-gradient(90deg,transparent,#000 var(--scroll-shadow-size),#000)",
            },
          }}
        >
          <ScrollArea.Content spaceY="4">
            <Flex gap="4" flexWrap="nowrap">
              {!loading
                ? engagingBooks.map((item, index) => (
                    <Box
                      width={"200px"}
                      height={"full"}
                      key={index}
                      cursor={"pointer"}
                      onClick={() => handleBookClick(item.isbn)}
                    >
                      <img
                        src={item.img_url_l}
                        key={index}
                        style={{ borderRadius: 6 }}
                      />
                    </Box>
                  ))
                : Array.from({ length: 10 }, (_, i) => (
                    <Skeleton key={i} variant={"shine"} loading={true} asChild>
                      <Box key={i} h="20rem" width={"200px"}>
                        Item {i + 1}
                      </Box>
                    </Skeleton>
                  ))}
            </Flex>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
      </ScrollArea.Root>
    </VStack>
  );
};

export default page;
