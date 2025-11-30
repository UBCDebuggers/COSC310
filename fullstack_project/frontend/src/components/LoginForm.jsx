"use client";
import {
  Flex,
  HStack,
  VStack,
  Text,
  Input,
  Button,
  Container,
} from "@chakra-ui/react";
import React from "react";
import { VscBook } from "react-icons/vsc";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import AuthForm from "./AuthForm";
import "./style.css";

const LoginForm = () => {
  const [quote, setQuote] = React.useState({ quote: "", author: "" });

  const LoginFacts = [
    '"A reader lives a thousand lives before he dies . . . The man who never reads lives only one."',
    '"So many books, so little time."',
    '"A room without books is like a body without a soul."',
    '"You can never get a cup of tea large enough or a book long enough to suit me."',
    '"If you only read the books that everyone else is reading, you can only think what everyone else is thinking."',
  ];

  const authors = [
    "- George R.R. Martin",
    "- Frank Zappa",
    "- Marcus Tullius Cicero",
    "- C.S. Lewis",
    "- Haruki Murakami",
  ];

  React.useEffect(() => {
    const randomIndex = Math.floor(Math.random() * LoginFacts.length);
    setQuote({
      quote: LoginFacts[randomIndex],
      author: authors[randomIndex],
    });
  }, []);

  return (
    <Flex
      h="100vh"
      w="100vw"
      bgImage={"url(/Libr.gif)"}
      bgPosition="center"
      bgSize="cover"
      bgRepeat="no-repeat"
      justify="center"
      align="center"
      overflow="hidden"
    >
      <Flex
        w={["95%", "85%", "75%", "60%"]}
        maxW="1000px"
        maxH="90vh"
        backdropFilter="blur(5px)"
        borderRadius={"24px"}
        direction={["column", "column", "row"]}
        justify="center"
        align="center"
        bg="rgba(0, 0, 0, 0.55)"
        p={[6, 8, 10]}
        gap={[6, 8, 10]}
        boxShadow="0 4px 20px rgba(0,0,0,0.4)"
      >
        <Flex
          direction={["column", "column", "row"]}
          justify={"center"}
          align="center"
          overflowY="auto"
          overflowX="hidden"
          w="100%"
          h="100%"
          gap={[6, 8, 10]}
        >
          <VStack
            spacing={4}
            textAlign={"center"}
            flex="1"
            align="center"
            justify="center"
            maxW="400px"
            p={[2, 4]}
            color="white"
          >
            <Text
              fontSize={["3xl", "4xl", "5x1"]}
              mt={["0px", "300px", "0px"]}
              fontWeight={"bold"}
            >
              Welcome Back!
            </Text>

            <HStack spacing={2} mb={2}>
              <VscBook size={30} />
              <Text fontSize="sm" mt="12.5px">
                by The Debuggers
              </Text>
            </HStack>

            <Text
              fontSize={["mg", "lg", "xl"]}
              fontStyle="italic"
              px={2}
              maxW={"380px"}
              lineHeight="tall"
            >
              {quote.quote}
            </Text>
            <Text fontSize={"sm"} opacity={0.7} mb={6}>
              {quote.author}
            </Text>
            <Text fontSize={"sm"} opacity={0.8} mb={2}>
              Your entire library, just a click away. Search, filter, and
              reserve books effortlessly with your personal account.
            </Text>
          </VStack>

          {/* <Text fontSize={'lg'} alignSelf={'center'} maxW={'400px'}>{quote}</Text> */}
          <VStack
            spacing={6}
            w="100%"
            maxW="400px"
            flex="1"
            align={"center"}
            justify="center"
          >
            <AuthForm />
          </VStack>
        </Flex>
      </Flex>
    </Flex>
  );
};

export default LoginForm;
