"use client"
import { Button, Container, Field, Flex, Image, Input, Stack, Text } from "@chakra-ui/react"
import { PasswordInput, PasswordStrengthMeter } from "@/components/ui/password-input"
import React from 'react'
import AuthContext from "@/app/context/AuthContext"
import "./style.css"

const AuthForm = () => {
  const { login } = React.useContext(AuthContext)
  const [username, setUsername] = React.useState("")
  const [password, setPassword] = React.useState("")
    
  const handleSubmit = (e) => {
    e.preventDefault()
    login(username, password)
  };

  return (
        <Flex w={{ base: '75vw', md: '25vw'}} p={5} alignSelf={"center"} justifyContent={'center'}>
          <form onSubmit={handleSubmit}>
            <Stack align="flex-start" maxW="lg">
              <Text marginBottom={0} textStyle='4xl' fontFamily="Poppins, sans-serif">User Login</Text>
              <Text marginTop={0} textStyle="sm">Don't have an account? Sign Up</Text>

              <Field.Root invalid={false}>
                <Field.Label>Username</Field.Label>
                <Input variant={'subttle'} bg={'white/20'} name="username" borderRadius={20} onChange={(e) => setUsername(e.target.value)}/>
                <Field.ErrorText>{"hello"}</Field.ErrorText>
              </Field.Root>
    
              <Field.Root invalid={false}>
                <Field.Label>Password</Field.Label>
                <PasswordInput variant={'subtle'} bg={'white/20'} name="password" borderRadius={20} onChange={(e) => setPassword(e.target.value)}/>
                <Field.ErrorText>{"hello"}</Field.ErrorText>
              </Field.Root>

              <Button type="submit" borderRadius={20} marginTop="15px" w ={{base: '65vw', md: '20vw'}}>Login</Button>
              <Button variant={'link'} alignSelf={'center'} _hover={{fontStretch: ''}}>Forgot Password?</Button>
            </Stack>
          </form>
        </Flex>
        )
}

export default AuthForm