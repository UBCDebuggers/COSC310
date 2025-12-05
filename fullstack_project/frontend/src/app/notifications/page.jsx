"use client";

import React, { useEffect, useState, useContext } from "react";
import { useRouter } from "next/navigation";
import AuthContext from "../context/AuthContext";
import axios from "axios";
import { VStack, HStack, Text, Spinner, Badge } from "@chakra-ui/react";

export default function NotificationsPage() {
  const router = useRouter();
  const { user } = useContext(AuthContext);

  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.access_token) {
      router.push("/");
      return;
    }

    const fetchNotifications = async () => {
      try {
        const res = await axios.get(
          `http://localhost:8000/notifications/${user?.sub}`,
          {
            headers: { Authorization: `Bearer ${user?.access_token}` },
          }
        );

        setNotifications(res.data || []);
      } catch (err) {
        console.error("Error fetching notifications:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, [user]);

  if (loading) {
    return (
      <VStack w="100%" p={5}>
        <Text fontWeight="bold" fontSize="5xl">
          Notifications
        </Text>
        <Spinner size="xl" />
      </VStack>
    );
  }

  return (
    <VStack w="100%" alignItems="flex-start" p={5} gap={4}>
      <Text fontWeight="bold" fontSize="5xl">
        Notifications
      </Text>

      {notifications.length === 0 && (
        <Text fontSize="lg" color="gray.500">
          You have no notifications!! YAYY!!
        </Text>
      )}

      {notifications.map((notif) => (
        <HStack
          key={notif.notificationid}
          w="100%"
          p={3}
          borderRadius="lg"
          borderWidth="1px"
          _hover={{ bg: "gray.100" }}
        >
          {/* NEW badge */}
          {!notif.isread && (
            <Badge colorPalette="red" mr={2}>
              NEW
            </Badge>
          )}

          <VStack align="flex-start" spacing={0}>
            <Text fontWeight="bold" fontSize="lg">
              {notif.message}
            </Text>

            <Text fontSize="sm" color="gray.600">
              Type: {notif.type} • Category: {notif.category}
            </Text>

            <Text fontSize="xs" color="gray.500">
              {new Date(notif.timestamp).toLocaleString()}
            </Text>
          </VStack>
        </HStack>
      ))}
    </VStack>
  );
}
