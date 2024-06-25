import {
    Badge,
    Container,
    Heading,
    SkeletonText,
    Table,
    TableContainer,
    Tbody,
    Td,
    Th,
    Thead,
    Tr,
    useDisclosure,
  } from "@chakra-ui/react"
  import { useQueryClient, useSuspenseQuery } from "@tanstack/react-query"
  import { createFileRoute } from "@tanstack/react-router"
  
  import { Suspense, useState } from "react"
  import { type UserPublic, RequestService } from "../../client"
  import ViewUser from "../../components/User/ViewUser"
  
  export const Route = createFileRoute("/_layout/friends")({
    component: User,
  })
  
  const MembersTableBody = () => {
    const queryClient = useQueryClient()
    const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
    const [selectedUser, setSelectedUser] = useState({});
  
    const { data: users } = useSuspenseQuery({
      queryKey: ["friends"],
      queryFn: () => RequestService.readFriends(),
    })

    const viewUserModal = useDisclosure()

    const selectUser = (user: UserPublic) => {
      setSelectedUser(user)
      viewUserModal.onOpen()
    }

    const processDate = (date: Date) => {
        return date.toLocaleString()
    }
  
    return (
      <>
        <Tbody>
          {users.map((user) => (
            <Tr key={user.id} onClick={() => selectUser(user)}>
              <Td color={!user.full_name ? "ui.dim" : "inherit"}>
                {user.full_name || "N/A"}
                {currentUser?.id === user.id && (
                  <Badge ml="1" colorScheme="teal">
                    You
                  </Badge>
                )}
              </Td>
              <Td>{user.email}</Td>
              <Td>{processDate(new Date(user.friends_since))}</Td>
            </Tr>
          ))}
        </Tbody>
        <ViewUser
            user={selectedUser as UserPublic}
            isOpen={viewUserModal.isOpen}
            onClose={viewUserModal.onClose}
            isFriendList={true}
        />
      </>
    )
  }
  
  const MembersBodySkeleton = () => {
    return (
      <Tbody>
        <Tr>
          {new Array(5).fill(null).map((_, index) => (
            <Td key={index}>
              <SkeletonText noOfLines={1} paddingBlock="16px" />
            </Td>
          ))}
        </Tr>
      </Tbody>
    )
  }
  
  function User() {
    return (
      <Container maxW="full">
        <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
          Friends List
        </Heading>
        <TableContainer>
          <Table fontSize="md" size={{ base: "sm", md: "md" }}>
            <Thead>
              <Tr>
                <Th width="20%">Full name</Th>
                <Th width="50%">Email</Th>
                <Th width="10%">Friends since</Th>
              </Tr>
            </Thead>
            <Suspense fallback={<MembersBodySkeleton />}>
              <MembersTableBody />
            </Suspense>
          </Table>
        </TableContainer>
      </Container>
    )
  }
  