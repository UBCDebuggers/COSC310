"use client";

import React, { useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Box, Button, Container, Field, Heading, Input, Spinner, Stack, Text, VStack } from "@chakra-ui/react";
import AuthContext from "@/app/context/AuthContext";

const AccountPage = () => {
  const router = useRouter();
  const { logout } = useContext(AuthContext);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const [userId, setUserId] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [department, setDepartment] = useState("");
  const [age, setAge] = useState(0);
  const [username, setUsername] = useState("");
  const [firstname, setFirstname] = useState("");
  const [lastname, setLastname] = useState("");

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) {
      setError("No access token found. Please log in.");
      setLoading(false);
      return;
    }

    let payload = null;
    try {
      payload = JSON.parse(atob(token.split(".")[1]));
    } catch (e) {
      setError("Invalid token. Please log in again.");
      setLoading(false);
      return;
    }

    const currentUserId = payload?.sub;
    const adminFlag = Boolean(payload?.admin);

    if (!currentUserId) {
      setError("Unable to determine current user.");
      setLoading(false);
      return;
    }

    setUserId(currentUserId);
    setIsAdmin(adminFlag);

    const fetchUser = async () => {
      try {
        const res = await fetch(`http://localhost:8000/users/get/${encodeURIComponent(currentUserId)}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body?.detail || `Failed to load user (${res.status})`);
        }

        const data = await res.json();
        setEmail(data.email || "");
        setPassword(data.hash_password || "");
        setDepartment(data.department || "");
        setAge(Number(data.age) || 0);
        setUsername(data.username || "");
        setFirstname(data.firstname || "");
        setLastname(data.lastname || "");
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("No access token found. Please log in.");
      setSaving(false);
      return;
    }

    const payload = {
      email,
      password,
      is_admin: isAdmin,
      department,
      age: Number(age) || 0,
      username,
      firstname,
      lastname,
    };

    try {
      const res = await fetch("http://localhost:8000/users/update", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail || `Failed to update (${res.status})`);
      }

      setSuccess("Profile updated.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!isAdmin) {
      setError("Admin access required to delete a user.");
      return;
    }

    setDeleting(true);
    setError(null);
    setSuccess(null);
    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("No access token found. Please log in.");
      setDeleting(false);
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/users/${encodeURIComponent(userId)}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail || `Failed to delete (${res.status})`);
      }

      setSuccess("Account deleted.");
      logout();
      router.push("/login");
    } catch (err) {
      setError(err.message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Container maxW="3xl" py={10}>
      <VStack align="stretch" spacing={6}>
        <Box>
          <Heading size="lg">Account</Heading>
          <Text color="gray.500">View and manage your profile.</Text>
        </Box>

        {loading ? (
          <Stack align="center" py={10}>
            <Spinner size="lg" />
            <Text>Loading account...</Text>
          </Stack>
        ) : (
          <>
            {error && (
              <Box borderWidth="1px" borderColor="red.500" borderRadius="md" p={3} color="red.600">
                {error}
              </Box>
            )}
            {success && (
              <Box borderWidth="1px" borderColor="green.500" borderRadius="md" p={3} color="green.600">
                {success}
              </Box>
            )}

            <Box borderWidth="1px" borderRadius="md" p={6} bg="chakra-body-bg">
              <VStack spacing={4} align="stretch">
                <Field.Root>
                  <Field.Label>Username</Field.Label>
                  <Input value={username} onChange={(e) => setUsername(e.target.value)} />
                </Field.Root>

                <Field.Root>
                  <Field.Label>First Name</Field.Label>
                  <Input value={firstname} onChange={(e) => setFirstname(e.target.value)} />
                </Field.Root>

                <Field.Root>
                  <Field.Label>Last Name</Field.Label>
                  <Input value={lastname} onChange={(e) => setLastname(e.target.value)} />
                </Field.Root>

                <Field.Root>
                  <Field.Label>Age</Field.Label>
                  <Input type="number" value={age} onChange={(e) => setAge(e.target.value)} />
                </Field.Root>

                <Field.Root>
                  <Field.Label>Department</Field.Label>
                  <Input value={department} onChange={(e) => setDepartment(e.target.value)} />
                </Field.Root>

                <Field.Root>
                  <Field.Label>Email</Field.Label>
                  <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                </Field.Root>

                <Field.Root>
                  <Field.Label>Password</Field.Label>
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Leave as is to keep current password"
                  />
                </Field.Root>

            <Stack direction={{ base: "column", sm: "row" }} spacing={4} pt={2}>
              <Button colorPalette="blue" onClick={handleSave} isLoading={saving} flex={1}>
                Save Changes
              </Button>
              <Button variant="outline" onClick={() => router.push("/dashboard")} flex={1}>
                    Cancel
                  </Button>
                </Stack>
              </VStack>
            </Box>

            {isAdmin && (
              <Box borderWidth="1px" borderRadius="md" p={6} bg="chakra-body-bg">
                <VStack spacing={4} align="stretch">
                  <Heading size="md">Danger Zone</Heading>
                  <Text color="gray.500">Delete this account permanently.</Text>
                  <Button colorPalette="red" onClick={handleDelete} isLoading={deleting}>
                    Delete Account
                  </Button>
                </VStack>
              </Box>
            )}
          </>
        )}
      </VStack>
    </Container>
  );
};

export default AccountPage;
