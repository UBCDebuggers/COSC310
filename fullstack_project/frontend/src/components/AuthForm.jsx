"use client"
import { Button, Container, Field, Flex, Image, Input, Stack, Text } from "@chakra-ui/react"
import { PasswordInput, PasswordStrengthMeter } from "@/components/ui/password-input"
import React from 'react'
import AuthContext from "@/app/context/AuthContext"

const AuthForm = () => {
  const { login } = React.useContext(AuthContext)
  const [username, setUsername] = React.useState("")
  const [password, setPassword] = React.useState("")
    
  const handleSubmit = (e) => {
    e.preventDefault()
    login(username, password)
  };

  return (
        <Flex  border={"1px solid gray"} borderRadius={5} w={{ base: '75vw', md: '25vw'}} p={5} alignSelf={"center"} justifyContent={'center'}>
          <form onSubmit={handleSubmit}>
            <Stack gap="4" align="flex-start" maxW="lg">
                <Text fontWeight={'bold'} fontSize={'4xl'}>User Login</Text>

              <Field.Root invalid={false}>
                <Field.Label>Username</Field.Label>
                <Input variant={'subtle'} name="username" onChange={(e) => setUsername(e.target.value)}/>
                <Field.ErrorText>{"hello"}</Field.ErrorText>
              </Field.Root>
    
              <Field.Root invalid={false}>
                <Field.Label>Password</Field.Label>
                <PasswordInput variant={'subtle'} name="password" onChange={(e) => setPassword(e.target.value)}/>
                <Field.ErrorText>{"hello"}</Field.ErrorText>
              </Field.Root>

              <Button variant={'link'} alignSelf={'center'} _hover={{fontStretch: ''}}>Forgot Password?</Button>
    
              <Button type="submit" borderRadius={20} w ={{base: '65vw', md: '20vw'}}>Login</Button>
            </Stack>
          </form>
        </Flex>
        )
}

export default AuthForm