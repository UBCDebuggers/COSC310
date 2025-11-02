"use client"
import { AbsoluteCenter, Box, Flex, Image, Stack, HStack, VStack, Text } from "@chakra-ui/react"
import React, { useState, useEffect, useCallback } from 'react'
import { VscBook } from "react-icons/vsc";

import AuthForm from "./AuthLoginForm"
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
    <Flex h="100vh" w="100vw" bgImage={'url(/Libr.gif)'} bgPosition="center" bgSize="cover" bgRepeat="no-repeat" justify="center" align="center" overflow="hidden">
      <Flex w = {["95%", "85%", "75%", "60%"]} maxW="1000px" maxH="90vh" backdropFilter="blur(5px)" overflowY="auto" borderRadius={"24px"} direction={["column", "column", "row"]} justify="center" align="center" bg="rgba(0, 0, 0, 0.55)" p={[6, 8, 10]} gap={[6, 8, 10]} boxShadow="0 4px 20px rgba(0,0,0,0.4)">
          <VStack spacing={4} textAlign={"center"} flex="1" align="center" justify="center" maxW="400px" p={[2, 4]}>
            <Text fontSize={["3xl", "4xl", "5x1"]} mt={["0px", "200px", "0px"]} fontWeight={'bold'}>Welcome Back!</Text>
            
            <HStack>
              <VscBook size={40}/> 
              <Text fontSize="sm" fontWeight="semibold" mt="10px">by The Debuggers</Text>
            </HStack>

            <Text fontSize={["sm", "md", "lg"]} fontStyle="italic" px={2} maxW={'380px'} lineHeight="tall">{quote}</Text> 
            <Text fontSize={'sm'} opacity={0.8}>~Description~</Text>
          </VStack>

          {/* <Text fontSize={'lg'} alignSelf={'center'} maxW={'400px'}>{quote}</Text> */}
          <VStack spacing={6} w="100%" maxW="400px" flex="1" align={"center"} justify="center">
            <AuthForm />
          </VStack>
      </Flex>
    </Flex>
  )
}

export default LoginForm