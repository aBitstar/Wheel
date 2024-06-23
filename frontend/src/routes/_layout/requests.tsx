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
  import { useSuspenseQuery } from "@tanstack/react-query"
  import { createFileRoute } from "@tanstack/react-router"
  
  import { Suspense } from "react"
  import { ErrorBoundary } from "react-error-boundary"
  import { RequestService } from "../../client"
  import RequestActions from "../../components/Requests/RequestActions"
  
  export const Route = createFileRoute("/_layout/requests")({
    component: Requests,
  })
  
  function RequestsTableBody() {
    const { data: requests } = useSuspenseQuery({
      queryKey: ["requests"],
      queryFn: () => RequestService.getRequests(),
    })
    console.log(requests);
  
    return (
      <Tbody>
        {requests.map((request, index) => (
          <Tr key={request.id}>
            <Td>{index + 1}</Td>
            <Td>{request.sender_name}</Td>
            <Td>{request.sender_email}</Td>
            <Td>
              <RequestActions />
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
  