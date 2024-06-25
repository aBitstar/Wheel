import {
    Container,
    Flex,
    Heading,
    Skeleton,
    Table,
    TableContainer,
    Tbody,
    Td,
    Th,
    Thead,
    Tr,
  } from "@chakra-ui/react"
  import { useMutation, useQueryClient, useSuspenseQuery } from "@tanstack/react-query"
  import { createFileRoute } from "@tanstack/react-router"
  
  import { Suspense, useState } from "react"
  import { ErrorBoundary } from "react-error-boundary"
  import { ApiError, RequestService, UserPublic } from "../../client"
  import RequestActions from "../../components/Requests/RequestActions"
  import { AcceptFriends } from "../../client/models"
import useCustomToast from "../../hooks/useCustomToast"
  
  export const Route = createFileRoute("/_layout/requests")({
    component: Requests,
  })
  
  function RequestsTableBody() {
    const { data: requests } = useSuspenseQuery({
      queryKey: ["requests"],
      queryFn: () => RequestService.getRequests(),
    })

    const queryClient = useQueryClient()
    const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

    const [FriendRequests, setFriendRequests] = useState(requests)

    const showToast = useCustomToast()

    const mutation = useMutation({
      mutationFn: (data: AcceptFriends) =>
        RequestService.acceptRequest(data),
      onSuccess: (data) => {
        showToast("Congratulations!", "You accepted Friend Request.", "success")
        // reset()
        setFriendRequests(data)
      },
      onError: (err: ApiError) => {
        const errDetail = (err.body as any)?.detail
        showToast("Something went wrong.", `${errDetail}`, "error")
      },
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["friend_requests"] })
      },
    })

    const declineMutation = useMutation({
      mutationFn: (data: AcceptFriends) =>
        RequestService.declineRequest(data),
      onSuccess: (data) => {
        showToast("Oops!", "You declined Friend Request.", "warning")
        // reset()
        setFriendRequests(data)
      },
      onError: (err: ApiError) => {
        const errDetail = (err.body as any)?.detail
        showToast("Something went wrong.", `${errDetail}`, "error")
      },
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["friend_requests"] })
      },
    })

    const onAccept = async (sender_id: number, receiver_id = currentUser?.id) => {
      
      mutation.mutate(
        {sender_id, receiver_id}
      )
    }

    const onDecline = async (sender_id: number, receiver_id = currentUser?.id) => {
      declineMutation.mutate(
        {sender_id, receiver_id}
      )
    }
  
    return (
      <Tbody>
        {FriendRequests.map((request, index) => (
          <Tr key={request.id}>
            <Td>{index + 1}</Td>
            <Td>{request.sender_name}</Td>
            <Td>{request.sender_email}</Td>
            <Td>
              <RequestActions onAccept={() => onAccept(request.sender_id)} onDecline={() => onDecline(request.sender_id)}/>
            </Td>
          </Tr>
        ))}
      </Tbody>
    )
  }
  function RequestsTable() {
    return (
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Sender</Th>
              <Th>Sender Email</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <ErrorBoundary
            fallbackRender={({ error }) => (
              <Tbody>
                <Tr>
                  <Td colSpan={4}>Something went wrong: {error.message}</Td>
                </Tr>
              </Tbody>
            )}
          >
            <Suspense
              fallback={
                <Tbody>
                  {new Array(5).fill(null).map((_, index) => (
                    <Tr key={index}>
                      {new Array(4).fill(null).map((_, index) => (
                        <Td key={index}>
                          <Flex>
                            <Skeleton height="20px" width="20px" />
                          </Flex>
                        </Td>
                      ))}
                    </Tr>
                  ))}
                </Tbody>
              }
            >
              <RequestsTableBody />
            </Suspense>
          </ErrorBoundary>
        </Table>
      </TableContainer>
    )
  }
  
  function Requests() {
    return (
      <Container maxW="full">
        <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
          Requests Management
        </Heading>
  
        <RequestsTable />
      </Container>
    )
  }
  