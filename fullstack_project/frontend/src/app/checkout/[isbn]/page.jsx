"use client";
import React, { useContext, useState, useEffect } from "react";
import AuthContext from "../../context/AuthContext";
import { useRouter, useParams } from "next/navigation";
import { Flex, Image, Progress, Text, VStack, Button } from "@chakra-ui/react";
import axios from "axios";

const page = () => {
  const { user } = useContext(AuthContext);
  const router = useRouter();
  const params = useParams();
  const isbn = params?.isbn;
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);

  const handleReserve = () => {
    if (!!!user?.sub) {
      router.push("/");
      return;
    }
    const reserveBook = async () => {
      try {
        const res = await axios.post(
          `http://localhost:8000/library/borrow?reservation_id=new`,
          {
            userid: "null",
            isbn: isbn,
          },
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${user?.access_token}`,
            },
          }
        );
        if (res.status != 200) throw Error("Could not reserve book");
        router.push("/dashboard");
      } catch (err) {
        console.log(err);
      }
    };
    reserveBook();
  };

  useEffect(() => {
    if (!!!user?.sub) {
      router.push("/");
      return;
    }
    const fetchBook = async () => {
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:8000/books/${isbn}`);
        const resBook = await res.json();
        if (!res.ok) throw new Error("Could not fetch book");
        setBook(resBook);
      } catch (err) {
        console.log(err);
      } finally {
        setLoading(false);
      }
      console.log(book);
    };
    fetchBook();
  }, [isbn]);

  return (
    <VStack w="100vw" h="100vh" alignItems={"center"}>
      {loading ? (
        <Progress.Root value={null} w={"full"}>
          <Progress.Track>
            <Progress.Range />
          </Progress.Track>
        </Progress.Root>
      ) : (
        <Flex
          backdropFilter="blur(5px)"
          bg={{ _dark: "gray.800", _light: "gray.300" }}
          px={10}
          py={5}
          borderRadius={10}
          minW={"30vw"}
          minH={"30vh"}
          maxW="60vw"
          gap={10}
          alignItems="center"
          alignSelf={"center"}
        >
          <Image src={book?.img_url_l}></Image>
          <VStack alignItems="flex-start">
            <Text fontWeight="bold" fontSize={24}>
              {book?.title}
            </Text>

            <Text color="gray.500">by {book?.author}</Text>
            <Text color="gray.500">Published: {book?.year_of_publication}</Text>
            <Text color="gray.500">ISBN: {book?.isbn}</Text>
            <Flex gap={10} alignItems={"flex-end"} w={"full"}>
              <Button
                colorPalette={"red"}
                borderRadius={10}
                onClick={() => {
                  router.back();
                }}
              >
                Take me back
              </Button>
              <Button
                colorPalette={"blue"}
                borderRadius={10}
                onClick={handleReserve}
              >
                Confirm Reservation
              </Button>
            </Flex>
          </VStack>
        </Flex>
      )}
    </VStack>
  );
};

export default page;
