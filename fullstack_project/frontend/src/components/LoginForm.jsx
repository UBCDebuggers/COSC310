import { Box, Flex, Image, Stack, Text } from "@chakra-ui/react"
import React from 'react'

import AuthForm from "./AuthForm"

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
    <Flex w={'full'} h={'100vh'} border={"1px solid gray"} gap={3}>
      {/* display an image on the left side of the login form unless the screen is small */}
      <Image src="/login.png" alt="Login Illustration" objectFit="cover" flex={1} maxW={"50vw"} display={{md: 'block', base: 'none'}} />
      <Stack position={'absolute'} bottom={'50%'} left={'5%'} color={'white'}>
        <Text fontSize={'6xl'} fontWeight={'bold'}>Welcome Back!</Text>
        <Text fontSize={'lg'} alignSelf={'center'} maxW={'30vw'}>{quote}</Text>
      </Stack>

      <Flex justifyContent={'center'} w={'full'}>
        <AuthForm />
      </Flex>
    </Flex>
  )
}

export default LoginForm