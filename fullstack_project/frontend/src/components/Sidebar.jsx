"use client";
import React, { useContext } from "react";
import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import AuthContext from "@/app/context/AuthContext";
import { useColorMode } from "./ui/color-mode";
import {
  ClientOnly,
  IconButton,
  Skeleton,
  Flex,
  VStack,
  Combobox,
  Portal,
  Input,
  InputGroup,
  Avatar,
  Text,
  Spacer,
  ProgressCircle,
  Menu,
  Dialog,
  Button,
  Box,
} from "@chakra-ui/react";
import { LuMoon, LuSun } from "react-icons/lu";
import { BsPerson, BsGear, BsBoxArrowLeft } from "react-icons/bs";
import { FiSearch } from "react-icons/fi";
import { VscBook } from "react-icons/vsc";
import { BiSliderAlt } from "react-icons/bi";
import { CgArrowLongRight, CgClose } from "react-icons/cg";

const FilterMenu = ({
  tempAuthorFilter,
  setTempAuthorFilter,
  tempPublisherFilter,
  setTempPublisherFilter,
  tempMinYearFilter,
  setTempMinYearFilter,
  tempMaxYearFilter,
  setTempMaxYearFilter,
  handleApplyFilters,
}) => {
  return (
    <VStack gap={4}>
      <Dialog.CloseTrigger asChild>
        <Button variant={"ghost"} borderRadius={5} colorPalette={"red"}>
          <CgClose size={20} />
        </Button>
      </Dialog.CloseTrigger>
      <VStack gap={-2} w={"full"}>
        <Text alignSelf={"flex-start"} fontWeight={"bold"}>
          Author
        </Text>
        <Input
          value={tempAuthorFilter}
          placeholder="e.g. J. K. Rowling"
          onChange={(e) => setTempAuthorFilter(e.target.value)}
        />
      </VStack>
      <VStack gap={-2} w={"full"}>
        <Text alignSelf={"flex-start"} fontWeight={"bold"}>
          Publisher
        </Text>
        <Input
          value={tempPublisherFilter}
          placeholder="e.g. Penguin Books"
          onChange={(e) => setTempPublisherFilter(e.target.value)}
        />
      </VStack>
      <VStack gap={-2}>
        <Text alignSelf={"flex-start"} fontWeight={"bold"}>
          Publication Year
        </Text>
        <Flex justifyContent={"center"} gap={2}>
          <Input
            value={tempMinYearFilter}
            placeholder="min"
            onChange={(e) => setTempMinYearFilter(e.target.value)}
          />
          <Flex alignContent={"center"}>
            <CgArrowLongRight size={40} />
          </Flex>
          <Input
            value={tempMaxYearFilter}
            placeholder="max"
            onChange={(e) => setTempMaxYearFilter(e.target.value)}
          />
        </Flex>
      </VStack>
      <Button
        colorPalette="green"
        borderRadius={5}
        onClick={handleApplyFilters}
        alignSelf={"flex-end"}
      >
        Apply Filters
      </Button>
    </VStack>
  );
};

const Sidebar = ({ children }) => {
  const { toggleColorMode, colorMode } = useColorMode();
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = React.useContext(AuthContext);
  const { user } = useContext(AuthContext);

  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [authorFilter, setAuthorFilter] = useState("");
  const [publisherFilter, setPublisherFilter] = useState("");
  const [minYearFilter, setMinYearFilter] = useState("");
  const [maxYearFilter, setMaxYearFilter] = useState("");

  const [tempAuthorFilter, setTempAuthorFilter] = useState("");
  const [tempPublisherFilter, setTempPublisherFilter] = useState("");
  const [tempMinYearFilter, setTempMinYearFilter] = useState("");
  const [tempMaxYearFilter, setTempMaxYearFilter] = useState("");

  const handleBookClick = (isbn) => {
    router.push(`/book/${isbn}`);
  };

  const handleBack = () => {
    router.back();
  };

  const filteredBooks = React.useMemo(() => {
    return books.filter((b) =>
      b.label.toLowerCase().includes(query.toLowerCase())
    );
  }, [books, query]);

  const handleInputChange = (details) => {
    setQuery(details.inputValue);
  };

  const handleApplyFilters = () => {
    setAuthorFilter(tempAuthorFilter);
    setPublisherFilter(tempPublisherFilter);
    setMinYearFilter(tempMinYearFilter);
    setMaxYearFilter(tempMaxYearFilter);
  };

  useEffect(() => {
    const params = new URLSearchParams();
    if (authorFilter) params.append("author", authorFilter);
    if (publisherFilter) params.append("publisher", publisherFilter);
    if (minYearFilter) params.append("publish_date_min", minYearFilter);
    if (maxYearFilter) params.append("publish_date_max", maxYearFilter);

    console.log("Fetching books with params:", params.toString());
    if (!query) {
      setBooks([]);
      return;
    }
    setLoading(true);

    const timeout = setTimeout(async function fetchBooks() {
      const res = await fetch(
        `http://localhost:8000/books/search/${encodeURIComponent(query)}?` +
          params.toString()
      );
      const data = await res.json();

      const formatted = data.map((book) => ({
        label: book.title,
        value: book.isbn,
        img: book.img_url_m,
        author: book.author,
      }));
      console.log("Fetched books:", formatted);

      setBooks(formatted);
      setLoading(false);
    }, 300);

    return () => clearTimeout(timeout);
  }, [
    query,
    authorFilter,
    publisherFilter,
    minYearFilter,
    maxYearFilter,
    user,
  ]);

  return (
    <>
      {pathname != "/" ? (
        <VStack w="100vw" h="100vh" overflowX={"hidden"}>
          <Flex
            p={4}
            gap={2}
            w={"100vw"}
            borderBottomWidth={2}
            borderColor={"grey.300"}
          >
            <Flex
              alignSelf={"center"}
              onClick={handleBack}
              _hover={{ textDecoration: "underline", color: "gray.800" }}
              cursor={"pointer"}
            >
              <VscBook size={70} />
              <Text fontSize={"2xl"} fontWeight="bold" alignSelf={"center"}>
                BookVerse
              </Text>
            </Flex>

            <Spacer w="15vw" />

            <Combobox.Root
              items={books}
              w={"50vw"}
              size="lg"
              variant={"subtle"}
              alignSelf={"center"}
              onInputValueChange={handleInputChange}
            >
              <Combobox.Control>
                <InputGroup startElement={<FiSearch />}>
                  <Combobox.Input asChild>
                    <Input placeholder="Search..." borderRadius={20} />
                  </Combobox.Input>
                </InputGroup>
                <Combobox.IndicatorGroup>
                  <Combobox.ClearTrigger />
                </Combobox.IndicatorGroup>
              </Combobox.Control>

              <Portal>
                <Combobox.Positioner>
                  <Combobox.Content>
                    <Combobox.Empty />
                    {loading && (
                      <Flex p={3} justifyContent="center">
                        <Text fontWeight="bold" mr={2}>
                          Searching...
                        </Text>
                        <ProgressCircle.Root value={null} size="xs">
                          <ProgressCircle.Circle>
                            <ProgressCircle.Track />
                            <ProgressCircle.Range strokeLinecap="round" />
                          </ProgressCircle.Circle>
                        </ProgressCircle.Root>
                      </Flex>
                    )}

                    {!loading && books.length === 0 && (
                      <Combobox.Empty>No books found</Combobox.Empty>
                    )}

                    {!loading &&
                      books.map((item) => (
                        <Combobox.Item
                          key={item.value}
                          item={item}
                          onClick={() => handleBookClick(item.value)}
                        >
                          <Flex gap={2} align="center">
                            <img
                              src={item.img}
                              style={{ width: 40, height: 70, borderRadius: 6 }}
                            />
                            <Flex direction="column">
                              <Text fontWeight="medium">{item.label}</Text>
                              <Text fontSize="sm" color="gray.500">
                                {item.author}
                              </Text>
                            </Flex>
                          </Flex>
                        </Combobox.Item>
                      ))}
                  </Combobox.Content>
                </Combobox.Positioner>
              </Portal>
            </Combobox.Root>

            <Dialog.Root>
              <ClientOnly fallback={<Skeleton boxSize="8" />}>
                <Dialog.Trigger asChild>
                  <IconButton
                    alignSelf={"center"}
                    variant={"ghost"}
                    size={"lg"}
                    borderRadius={4}
                  >
                    <BiSliderAlt />
                  </IconButton>
                </Dialog.Trigger>
              </ClientOnly>
              <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                  <Dialog.Content>
                    <Dialog.Header>
                      <Dialog.Title fontWeight={"bold"}>
                        Filter Books
                      </Dialog.Title>
                    </Dialog.Header>
                    <Dialog.Body spaceY="4">
                      <FilterMenu
                        tempAuthorFilter={tempAuthorFilter}
                        setTempAuthorFilter={setTempAuthorFilter}
                        tempPublisherFilter={tempPublisherFilter}
                        setTempPublisherFilter={setTempPublisherFilter}
                        tempMinYearFilter={tempMinYearFilter}
                        setTempMinYearFilter={setTempMinYearFilter}
                        tempMaxYearFilter={tempMaxYearFilter}
                        setTempMaxYearFilter={setTempMaxYearFilter}
                        handleApplyFilters={handleApplyFilters}
                      />
                    </Dialog.Body>
                  </Dialog.Content>
                </Dialog.Positioner>
              </Portal>
            </Dialog.Root>

            <Flex justifyContent={"flex-end"} w={"20vw"} gap={4}>
              <ClientOnly fallback={<Skeleton boxSize="8" />}>
                <IconButton
                  alignSelf={"center"}
                  onClick={toggleColorMode}
                  variant={"ghost"}
                  size={"lg"}
                  borderRadius={4}
                >
                  {colorMode === "light" ? <LuSun /> : <LuMoon />}
                </IconButton>
              </ClientOnly>
              <Menu.Root positioning={{ placement: "bottom-end" }}>
                <Menu.Trigger rounded="full" focusRing="outside">
                  <Avatar.Root
                    size={"xl"}
                    colorPalette={"blue"}
                    alignSelf={"center"}
                    cursor={"pointer"}
                    disabled={!!user?.sub}
                  >
                    <Avatar.Fallback name={user?.username} />
                    <Avatar.Image />
                  </Avatar.Root>
                </Menu.Trigger>
                <Portal>
                  <Menu.Positioner>
                    <Menu.Content>
                      <Menu.Item
                        value="account"
                        onClick={() => router.push("/account")}
                      >
                        <Flex
                          gap={2}
                          w={"full"}
                          borderBottomWidth={1}
                          borderColor={"grey.300"}
                        >
                          <BsPerson size={25} />
                          <Text fontWeight={"bold"}>Account</Text>
                        </Flex>
                      </Menu.Item>
                      <Menu.Item
                        value="settings"
                        justifyContent={"center"}
                        onClick={() => router.push("/settings")}
                      >
                        <Flex
                          gap={2}
                          w={"full"}
                          borderBottomWidth={1}
                          borderColor={"grey.300"}
                        >
                          <BsGear size={25} />
                          <Text fontWeight={"bold"}>Settings</Text>
                        </Flex>
                      </Menu.Item>
                      <Menu.Item
                        value="logout"
                        onClick={() => {
                          logout;
                          router;
                        }}
                      >
                        <Flex
                          gap={2}
                          w={"full"}
                          borderBottomWidth={1}
                          borderColor={"grey.300"}
                        >
                          <BsBoxArrowLeft size={25} />
                          <Text fontWeight={"bold"}>Logout</Text>
                        </Flex>
                      </Menu.Item>
                      <Menu.Item></Menu.Item>
                    </Menu.Content>
                  </Menu.Positioner>
                </Portal>
              </Menu.Root>
            </Flex>
          </Flex>
          <Flex direction="column" flex={1} w="100%">
            {children}
            <Spacer />
            <Flex
              justifyContent={"center"}
              p={4}
              gap={5}
              w={"100%"}
              borderColor={"grey.300"}
              borderTop="1px"
              mt={10}
              bg={{base: "white", _dark: "gray.950"}}
            >
              <Flex gap={2}>
                <Box
                  cursor={"pointer"}
                  _hover={{ color: "gray.800" }}
                  color={"gray.400"}
                >
                  <VscBook size={20} />
                </Box>
                <Text alignSelf={"center"} color={"gray.400"}>
                  © 2025 UBCDebuggers, org.
                </Text>
              </Flex>
              <Text
                alignSelf={"center"}
                _hover={{ textDecoration: "underline" }}
                cursor={"pointer"}
                color={"gray.400"}
              >
                Contact
              </Text>
              <Text
                alignSelf={"center"}
                _hover={{ textDecoration: "underline" }}
                cursor={"pointer"}
                color={"gray.400"}
              >
                Terms
              </Text>
            </Flex>
          </Flex>
        </VStack>
      ) : (
        <Box overflowX={"hidden"}>{children}</Box>
      )}
    </>
  );
};

export default Sidebar;
