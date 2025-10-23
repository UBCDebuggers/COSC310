import { Button, Container, Field, Flex, Image, Input, Stack, Text } from "@chakra-ui/react"
import { PasswordInput, PasswordStrengthMeter } from "@/components/ui/password-input"
import { useForm } from "react-hook-form"
import React from 'react'

const AuthForm = () => {

    const { register, handleSubmit, formState: { errors } } = useForm()
    
    const onSubmit = handleSubmit((data) => console.log(data))

  return (
        <Flex  border={"1px solid gray"} borderRadius={5} w={{ base: '75vw', md: '25vw'}} p={5} alignSelf={"center"} justifyContent={'center'}>
          <form onSubmit={onSubmit}>
            <Stack gap="4" align="flex-start" maxW="lg">
                <Text fontWeight={'bold'} fontSize={'4xl'}>User Login</Text>

              <Field.Root invalid={!!errors.username}>
                <Field.Label>Username</Field.Label>
                <Input variant={'subtle'} {...register("username")} />
                <Field.ErrorText>{errors.username?.message}</Field.ErrorText>
              </Field.Root>
    
              <Field.Root invalid={!!errors.password}>
                <Field.Label>Password</Field.Label>
                <PasswordInput variant={'subtle'} {...register("password")} />
                <Field.ErrorText>{errors.password?.message}</Field.ErrorText>
              </Field.Root>

              <Button variant={'link'} alignSelf={'center'} _hover={{fontStretch: ''}}>Forgot Password?</Button>
    
              <Button type="submit" borderRadius={20} w ={{base: '65vw', md: '20vw'}}>Login</Button>
            </Stack>
          </form>
        </Flex>
        )
}

export default AuthForm