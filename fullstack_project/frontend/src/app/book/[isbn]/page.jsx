"use client";

import {
  VStack,
  Flex,
  Image,
  Text,
  ProgressCircle,
  RatingGroup,
  ScrollArea,
  Button,
  IconButton,
  Avatar,
  Input,
  Dialog,
  Portal,
  Box,
} from "@chakra-ui/react";

import React, {
  useEffect,
  useState,
  useContext,
  useCallback,
  useMemo,
} from "react";
import { useRouter, useParams } from "next/navigation";
import AuthContext from "../../context/AuthContext";
import Comment from "@/components/Comment";
import { IoMdCheckmark } from "react-icons/io";
import { FaXmark } from "react-icons/fa6";
import { MdAdd } from "react-icons/md";
import { CgClose } from "react-icons/cg";
import { ImEnter } from "react-icons/im";
import axios from "axios";

const ReviewBox = React.memo(function ReviewBox({
  user,
  userReview,
  setUserReview,
  userRating,
  setUserRating,
  onSubmit,
}) {
  return (
    <Flex
      w="full"
      backdropFilter="blur(5px)"
      bg={{ _dark: "gray.800", _light: "gray.300" }}
      px={5}
      py={5}
      borderRadius={10}
      gap={2}
      alignItems={"center"}
      mb={5}
    >
      <Avatar.Root size="2xl" colorPalette={"blue"}>
        <Avatar.Fallback name={user?.username} />
      </Avatar.Root>

      <VStack w="full">
        <Input
          placeholder="Add a review..."
          w="full"
          variant={"subtle"}
          borderRadius={20}
          value={userReview}
          onChange={(e) => setUserReview(e.target.value)}
        />

        <RatingGroup.Root
          count={5}
          value={userRating}
          onValueChange={(val) => setUserRating(val.value)}
          size="sm"
          gap="4"
          colorPalette={"orange"}
          alignSelf={"flex-start"}
        >
          <RatingGroup.HiddenInput />
          <RatingGroup.Label>Rating: </RatingGroup.Label>
          <RatingGroup.Control />
        </RatingGroup.Root>
      </VStack>

      <Button
        colorPalette="blue"
        borderRadius={20}
        disabled={!user?.sub}
        onClick={onSubmit}
      >
        Post
      </Button>
    </Flex>
  );
});

const RatingsList = React.memo(function RatingsList({ ratings, loading }) {
  if (!ratings || ratings.length === 0)
    return loading ? (
      <VStack w={"full"} h={"full"}>
        <ProgressCircle.Root value={null} size="sm">
          <ProgressCircle.Circle>
            <ProgressCircle.Track />
            <ProgressCircle.Range />
          </ProgressCircle.Circle>
        </ProgressCircle.Root>
      </VStack>
    ) : (
      <Text>No Ratings Available</Text>
    );

  return (
    <>
      {ratings.map((rating, index) => (
        <Comment
          key={rating.userid + index}
          userid={rating.userid}
          desc={rating.description}
          rating={rating.rating}
          time={rating.timestamp}
        />
      ))}
    </>
  );
});

const Page = () => {
  const { user } = useContext(AuthContext);
  const router = useRouter();
  const params = useParams();
  const isbn = params?.isbn;

  const [book, setBook] = useState(null);
  const [ratings, setRatings] = useState([]);

  const [userRating, setUserRating] = useState(0);
  const [userReview, setUserReview] = useState("");

  const [loading, setLoading] = useState(true);
  const [reserved, setReserved] = useState(false);
  const [addedToWatchlist, setAddedToWatchlist] = useState(false);

  const [watchlistDialogOpen, setWatchlistDialogOpen] = useState(false);
  const [watchlistDialogStatus, setWatchlistDialogStatus] = useState(false);
  const [watchlistDialogMessage, setWatchlistDialogMessage] = useState("");

  const [waitlistDialogOpen, setDialogOpen] = useState(false);
  const [waitlistDialogStatus, setWaitlistDialogStatus] = useState(false);
  const [waitlistDialogMessage, setWaitlistDialogMessage] = useState("");

  const [recommended, setRecommended] = useState([]);
  const [showRecommend, setShowRecommend] = useState(false);

  const averageRating = useMemo(() => {
    if (!ratings || ratings.length === 0) return 0;
    const total = ratings.reduce((a, b) => a + b.rating, 0);
    return total / ratings.length;
  }, [ratings]);

  // NEW: Click handler for recommended books
  const handleBookClick = (isbn) => {
    router.push(`/book/${isbn}`);
  };

  useEffect(() => {
    if (!isbn) {
      router.push("/dashboard");
      return;
    }

    const fetchData = async () => {
      try {
        const [
          bookRes,
          ratingsJson,
          resData,
          watchlistJson,
          recommendedRes,
          resHistory,
        ] = await Promise.all([
          fetch(`http://localhost:8000/books/${isbn}`),
          fetch(`http://localhost:8000/ratings/isbn/${isbn}`).then((r) =>
            r.ok ? r.json() : []
          ),
          fetch(`http://localhost:8000/library/bookstatus/${isbn}`),
          user?.access_token
            ? axios
                .get("http://localhost:8000/watchlist", {
                  headers: { Authorization: `Bearer ${user.access_token}` },
                })
                .then((r) => r.data)
            : [],
          user?.access_token
            ? axios.get("http://localhost:8000/recommend", {
                headers: { Authorization: `Bearer ${user.access_token}` },
              })
            : null,
          user?.access_token
            ? axios.post(`http://localhost:8000/history/create/${isbn}`, {
                headers: { Authorization: `Bearer ${user.access_token}` },
              })
            : null,
        ]);
        console.log(resHistory);
        if (resData.ok) {
          const reserveJson = await resData.json();
          setReserved(reserveJson.status === "available");
        } else {
          setReserved(true);
        }

        // -------- FIXED RECOMMENDATION FETCHING --------
        if (recommendedRes && recommendedRes.status === 200) {
          setShowRecommend(true);

          const recommendedIsbns = recommendedRes.data;

          const books = await Promise.all(
            recommendedIsbns.map((isbn) =>
              fetch(`http://localhost:8000/books/${isbn}`).then((res) =>
                res.json()
              )
            )
          );

          setRecommended(books);
        }

        if (!bookRes.ok) throw new Error(`Book fetch failed ${bookRes.status}`);
        const bookData = await bookRes.json();

        setBook(bookData);
        setRatings(ratingsJson);

        setAddedToWatchlist(
          Array.isArray(watchlistJson) &&
            watchlistJson.some((item) => item.isbn === isbn)
        );
      } catch (err) {
        console.error("Fetch error:", err);
        setBook(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isbn, user]);

  const addRating = useCallback(async () => {
    try {
      await axios.post(
        "http://localhost:8000/ratings",
        {
          isbn,
          rating: Number(userRating * 2),
          description: userReview,
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${user?.access_token}`,
          },
        }
      );

      setUserReview("");
      setUserRating(0);

      const res = await fetch(
        `http://localhost:8000/ratings/isbn/${isbn}`
      ).then((r) => r.json());
      setRatings(res);
    } catch (err) {
      console.log(err);
    }
  }, [isbn, userRating, userReview, user]);

  const addToWatchlist = useCallback(
    async (item) => {
      try {
        const response = await axios.post("http://localhost:8000/watchlist", {
          isbn: item,
        });

        setWatchlistDialogStatus(true);
        setWatchlistDialogMessage(
          `“${response.data.title}” was added to your watchlist.`
        );
        setAddedToWatchlist(true);
      } catch (error) {
        setWatchlistDialogStatus(false);
        setWatchlistDialogMessage("Could not add to watchlist.");
      } finally {
        setWatchlistDialogOpen(true);
      }
    },
    [user]
  );

  const handleJoin = async () => {
    if (!user?.access_token) return router.push("/");

    try {
      await axios.post(
        `http://localhost:8000/library/borrow?reservation_id=new`,
        {
          userid: "null",
          isbn: isbn,
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${user?.access_token}`,
          },
        }
      );

      setWaitlistDialogStatus(true);
      setWaitlistDialogMessage("You have been added to the waitlist.");
    } catch (err) {
      console.log(err);
      setWaitlistDialogStatus(false);
      setWaitlistDialogMessage("Failed to join the waitlist.");
    } finally {
      setDialogOpen(true);
    }
  };

  const handleReserve = useCallback(() => {
    if (!user?.sub) return router.push("/");
    if (!reserved) return;
    router.push(`/checkout/${isbn}`);
  }, [reserved, user, isbn]);

  return (
    <VStack w="100vw" h="100vh" alignItems="flex-start" p={5}>
      <Flex w="full" h={"70vh"} gap={5} flex={1}>
        {/* ------------ BOOK INFO PANEL ------------ */}
        <Flex
          backdropFilter="blur(5px)"
          bg={{ _dark: "gray.800", _light: "gray.300" }}
          px={10}
          py={5}
          borderRadius={10}
          maxW="60vw"
          gap={10}
          alignItems="center"
          minW={"50vw"}
        >
          {!loading ? (
            book ? (
              <Flex gap={10} maxW={"55vw"} h="full" p={4}>
                <Image src={book.img_url_l} borderRadius={10} />
                <VStack alignItems="flex-start">
                  <Text fontWeight="bold" fontSize={24}>
                    {book.title}
                  </Text>

                  <RatingGroup.Root
                    count={5}
                    value={averageRating / 2}
                    readOnly
                    size="sm"
                    gap="4"
                    colorPalette="orange"
                  >
                    <RatingGroup.HiddenInput />
                    <RatingGroup.Label fontWeight={"bold"}>
                      Rating:
                    </RatingGroup.Label>
                    <RatingGroup.Control />
                  </RatingGroup.Root>

                  <Text color="gray.500">by {book.author}</Text>
                  <Text color="gray.500">
                    Published: {book.year_of_publication}
                  </Text>
                  <Text color="gray.500">ISBN: {book.isbn}</Text>

                  <Flex gap={10}>
                    <Button
                      colorPalette={reserved ? "green" : "red"}
                      onClick={handleReserve}
                      borderRadius={10}
                      disabled={!reserved}
                    >
                      {reserved ? (
                        <IoMdCheckmark size={20} />
                      ) : (
                        <FaXmark size={20} />
                      )}
                      {reserved ? "Reservation Available" : "On Loan"}
                    </Button>

                    {!reserved && (
                      <Button
                        variant={"outline"}
                        colorPalette={"blue"}
                        borderRadius={10}
                        onClick={handleJoin}
                      >
                        <ImEnter size={20} />
                        Join Waitlist
                      </Button>
                    )}
                  </Flex>

                  <IconButton
                    variant="ghost"
                    p={4}
                    colorPalette={"blue"}
                    disabled={addedToWatchlist}
                    onClick={() => addToWatchlist(book.isbn)}
                    alignSelf={"flex-start"}
                    mt={5}
                  >
                    {addedToWatchlist
                      ? "Added to Watchlist"
                      : "Add to Watchlist"}
                    {addedToWatchlist ? <IoMdCheckmark /> : <MdAdd />}
                  </IconButton>
                </VStack>
              </Flex>
            ) : (
              <Text>Content Unavailable</Text>
            )
          ) : (
            <ProgressCircle.Root value={null} size="sm" alignSelf={"center"}>
              <ProgressCircle.Circle>
                <ProgressCircle.Track />
                <ProgressCircle.Range />
              </ProgressCircle.Circle>
            </ProgressCircle.Root>
          )}
        </Flex>

        {/* ------------ RATINGS PANEL ------------ */}
        <ScrollArea.Root flex={2}>
          <ScrollArea.Viewport
            css={{
              "--scroll-shadow-size": "4rem",
              maskImage:
                "linear-gradient(#000,#000,transparent 0,#000 var(--scroll-shadow-size),#000 calc(100% - var(--scroll-shadow-size)),transparent)",
              "&[data-at-top]": {
                maskImage:
                  "linear-gradient(180deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
              },
              "&[data-at-bottom]": {
                maskImage:
                  "linear-gradient(0deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
              },
            }}
          >
            <ScrollArea.Content spaceY="4">
              <ReviewBox
                user={user}
                userReview={userReview}
                setUserReview={setUserReview}
                userRating={userRating}
                setUserRating={setUserRating}
                onSubmit={addRating}
              />
              <RatingsList ratings={ratings} loading={loading} />
            </ScrollArea.Content>
          </ScrollArea.Viewport>

          <ScrollArea.Scrollbar>
            <ScrollArea.Thumb />
          </ScrollArea.Scrollbar>
        </ScrollArea.Root>
      </Flex>

      {/* ---------- WATCHLIST DIALOG ---------- */}
      <Dialog.Root
        open={watchlistDialogOpen}
        onOpenChange={(d) => setWatchlistDialogOpen(d.open)}
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Dialog.Header>
                <Dialog.Title>
                  {watchlistDialogStatus
                    ? "Added to Watchlist"
                    : "Could Not Add"}
                </Dialog.Title>
              </Dialog.Header>

              <Dialog.Body>
                <Text>{watchlistDialogMessage}</Text>
              </Dialog.Body>

              <Dialog.Footer>
                {watchlistDialogStatus && (
                  <Button
                    colorPalette="green"
                    onClick={() => {
                      router.push("/watchlist");
                    }}
                  >
                    Open Watchlist
                  </Button>
                )}
                <Dialog.CloseTrigger asChild>
                  <Button variant="ghost" colorPalette="red">
                    <CgClose />
                  </Button>
                </Dialog.CloseTrigger>
              </Dialog.Footer>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>

      {/* ---------- WAITLIST DIALOG ---------- */}
      <Dialog.Root
        open={waitlistDialogOpen}
        onOpenChange={(d) => setDialogOpen(d.open)}
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Dialog.Header>
                <Dialog.Title>
                  {waitlistDialogStatus
                    ? "Joined Waitlist"
                    : "Could Not Join Waitlist"}
                </Dialog.Title>
              </Dialog.Header>

              <Dialog.Body>
                <Text>{waitlistDialogMessage}</Text>
              </Dialog.Body>

              <Dialog.Footer>
                {waitlistDialogStatus && (
                  <Button
                    colorPalette="green"
                    onClick={() => router.push("/waitlist")}
                  >
                    View My Waitlist
                  </Button>
                )}
                <Dialog.CloseTrigger asChild>
                  <Button variant="ghost" colorPalette="red">
                    <CgClose />
                  </Button>
                </Dialog.CloseTrigger>
              </Dialog.Footer>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>

      {/* ------------ RECOMMENDATION SECTION ------------ */}
      {showRecommend ? (
        <>
          <Text fontWeight={"bold"} fontSize={30} mt={5}>
            Recommended for you
          </Text>

          <Flex
            backdropFilter="blur(5px)"
            bg={{ _dark: "gray.800", _light: "gray.300" }}
            px={10}
            py={5}
            borderRadius={10}
            maxW="60vw"
            gap={10}
            alignItems="center"
            minW={"50vw"}
          >
            <Flex gap="4" flexWrap="nowrap">
              {recommended.map((item) => (
                <Box
                  key={item.isbn}
                  width="200px"
                  cursor="pointer"
                  onClick={() => handleBookClick(item.isbn)}
                >
                  <img
                    src={item.img_url_l}
                    style={{ borderRadius: 6, width: "100%" }}
                    alt={item.title}
                  />
                </Box>
              ))}
            </Flex>
          </Flex>
        </>
      ) : null}
    </VStack>
  );
};

export default Page;
