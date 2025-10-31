"use client"
import { AbsoluteCenter, Box, Flex, Image, Stack, HStack, VStack, Text } from "@chakra-ui/react"
import React from 'react'
import { VscBook } from "react-icons/vsc";

import AuthForm from "./AuthForm"
import "./style.css"

const LoginForm = () => {

  const [quote, setQuote] = React.useState("");

  const LoginFacts = [
    "\"A reader lives a thousand lives before he dies . . . The man who never reads lives only one.\"",
    "\"So many books, so little time.\"",
    "\"A room without books is like a body without a soul.\"",
    "\"You can never get a cup of tea large enough or a book long enough to suit me.\"",
    "\"If you only read the books that everyone else is reading, you can only think what everyone else is thinking.\""
  ]

  const authors = [
    "- George R.R. Martin",
    "- Frank Zappa",
    "- Marcus Tullius Cicero",
    "- C.S. Lewis",
    "- Haruki Murakami"
  ]

  
  React.useEffect(() => {
    const randomIndex = Math.floor(Math.random() * LoginFacts.length);
    setQuote(LoginFacts[randomIndex]);
  }, []);

  return (
    <Flex h="100vh" w="100vw" bgImage="url('/Libr.gif')" bgPosition="center" bgSize="100%" bgRepeat="no-repeat" justify="center" align="center" overflow="hidden">
      <Flex w = {'50%'} maxW={"75%"} borderRadius={100} flex="1" direction="column" justify="center" align="center" bg="rgba(0, 0, 0, 0.5)" color="white">
        <VStack>
        <HStack>
          <Stack spacing={6} textAlign={"center"}>
              <Text fontSize={'5xl'} fontWeight={'bold'}>Welcome Back!</Text>
            <HStack>
              <VscBook size={60}/> 
              <Text marginTop="10px">by The Debuggers</Text>
            </HStack>
            <Text fontSize={'lg'} alignSelf={'center'} maxW={'400px'}>{quote}</Text> 
            <Text fontSize={'md'} alignSelf={'center'} maxW={'400px'}>~Description~</Text>
          </Stack>
          <Stack spacing={6} textAlign={"center"}>
            {/* <Text fontSize={'lg'} alignSelf={'center'} maxW={'400px'}>{quote}</Text> */}
            <Box mt={8} w="100%" maxW="600px">
              <AuthForm />
            </Box>
          </Stack>
      
         </HStack>
         </VStack>
      </Flex>
    </Flex>
  )
}

export default LoginForm