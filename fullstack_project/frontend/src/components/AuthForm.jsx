"use client";
import {
  Button,
  Container,
  Field,
  Flex,
  Input,
  Stack,
  Text,
  VStack,
} from "@chakra-ui/react";
import { PasswordInput } from "@/components/ui/password-input";
import React from "react";
import AuthContext from "@/app/context/AuthContext";
import "./style.css";

const AuthForm = () => {
  const { login } = React.useContext(AuthContext);
  const { signup } = React.useContext(AuthContext);
  const [username, setUsername] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [isSignUp, setIsSignUp] = React.useState(false);
  const [email, setEmail] = React.useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isSignUp) {
      if (confirmPassword != password) {
        alert("Passwords don't match");
        return;
      }
      const user = {
        email: username,
        username: email,
        is_admin: false,
        department: "null",
        age: 0,
        firstname: "null",
        lastname: "null",
        password: password,
      };
      signup(user);
    } else {
      login(username, password);
    }
  };

  return (
    <Flex
      w={{ base: "75vw", md: "25vw" }}
      p={5}
      alignSelf={"center"}
      justifyContent={"center"}
    >
      <form onSubmit={handleSubmit}>
        <Stack align="center" maxW="lg" w="100%">
          <Container centerContent={true} mb={2}>
            <Text
              marginBottom={0}
              textStyle="4xl"
              fontFamily="Poppins, sans-serif"
            >
              User Login
            </Text>
            <Text marginTop={0} textStyle="sm">
              {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
              <Text
                as="span"
                color="white"
                textDecoration="underline"
                cursor="pointer"
                onClick={() => setIsSignUp(!isSignUp)}
                _hover={{ color: "gray.200" }}
              >
                {" "}
                {isSignUp ? "Login" : "Sign Up"}
              </Text>
            </Text>
          </Container>

          {isSignUp && (
            <Field.Root invalid={false}>
              <Field.Label>Username</Field.Label>
              <Input
                variant={"subtle"}
                bg={"white/20"}
                name="confirmPassword"
                borderRadius={20}
                onChange={(e) => setEmail(e.target.value)}
              />
              <Field.ErrorText>{"hello"}</Field.ErrorText>
            </Field.Root>
          )}

          <Field.Root invalid={false}>
            <Field.Label>Email</Field.Label>
            <Input
              variant={"subttle"}
              bg={"white/20"}
              name="username"
              borderRadius={20}
              onChange={(e) => setUsername(e.target.value)}
            />
            <Field.ErrorText>{"hello"}</Field.ErrorText>
          </Field.Root>

          <Field.Root invalid={false}>
            <Field.Label>Password</Field.Label>
            <PasswordInput
              variant={"subtle"}
              bg={"white/20"}
              name="password"
              borderRadius={20}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Field.ErrorText>{"hello"}</Field.ErrorText>
          </Field.Root>

          {isSignUp && (
            <Field.Root invalid={false}>
              <Field.Label>Confirm Password</Field.Label>
              <PasswordInput
                variant={"subtle"}
                bg={"white/20"}
                name="confirmPassword"
                borderRadius={20}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <Field.ErrorText>{"hello"}</Field.ErrorText>
            </Field.Root>
          )}

          <Button
            type="submit"
            borderRadius={20}
            marginTop="15px"
            w="100%"
            maxW={{ base: "65vw", md: "20vw" }}
            bg="white"
            color="black"
            _hover={{ bg: "gray.200" }}
          >
            {isSignUp ? "Sign Up" : "Login"}
          </Button>

          {!isSignUp && (
            <Button
              variant={"link"}
              alignSelf={"center"}
              mt={3}
              color="white"
              _hover={{ color: "gray.300", fontStretch: "" }}
            >
              Forgot Password?
            </Button>
          )}
        </Stack>
      </form>
    </Flex>
  );
};

export default AuthForm;
