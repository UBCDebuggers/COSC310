import { VStack, Avatar, Flex, Text, RatingGroup } from "@chakra-ui/react";
import React, { use, useEffect, useState } from "react";

const Comment = ({ userid, desc, rating, time }) => {
  const stars = rating > 0 ? rating / 2 : 0;

  return (
    <VStack
      w="full"
      alignItems={"flex-start"}
      backdropFilter="blur(5px)"
      bg={{ _dark: "gray.800", _light: "gray.300" }}
      px={10}
      py={5}
      borderRadius={10}
    >
      <Flex gap={4}>
        <Avatar.Root size="2xl" colorPalette={"blue"}>
          <Avatar.Fallback />
        </Avatar.Root>

        <VStack alignItems={"flex-start"}>
          <Text fontWeight={"bold"}>
            Anonymous {userid.substring(userid.length - 3)}
          </Text>

          <RatingGroup.Root
            colorPalette="orange"
            readOnly
            count={5}
            value={stars}
            defaultValue={2.5}
            size="xs"
          >
            <RatingGroup.HiddenInput />
            <RatingGroup.Control />
          </RatingGroup.Root>
        </VStack>

        <Text>{desc}</Text>

        <Text>{time ? new Date(time).toLocaleDateString() : ""}</Text>
      </Flex>
    </VStack>
  );
};

export default Comment;
