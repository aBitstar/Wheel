import {
    Button,
    Container,
    Text,
    Heading,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalFooter,
    ModalHeader,
    ModalOverlay,
    VStack,
    StackDivider,
  } from "@chakra-ui/react"
  import { useMutation, useQueryClient } from "@tanstack/react-query"
  
  import {
    type ApiError,
    type UserPublic,
    type SendRequest,
    RequestService,
  } from "../../client"
  import useCustomToast from "../../hooks/useCustomToast"

  
  interface ViewUserProps {
    user: UserPublic
    isOpen: boolean
    onClose: () => void
    isFriendList: boolean
  }
  
  const ViewUser = ({ user, isOpen, onClose, isFriendList }: ViewUserProps) => {
    const queryClient = useQueryClient()
    const showToast = useCustomToast()
    const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  
    const mutation = useMutation({
      mutationFn: (data: SendRequest) =>
        RequestService.sendRequest(data),
      onSuccess: () => {
        showToast("Success!", "Friend Request Sent successfully.", "success")
        // reset()
        onClose()
      },
      onError: (err: ApiError) => {
        const errDetail = (err.body as any)?.detail
        showToast("Something went wrong.", `${errDetail}`, "error")
        onClose()
      },
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["friend_requests"] })
      },
    })
  
    const onCancel = () => {
      // reset()
      onClose()
    }

    const sendRequest = (receiver_id: number) => {
      mutation.mutate(
        {sender_id: currentUser?.id, receiver_id: receiver_id}
      )
    }
  
    return (
      <>
        <Modal
          isOpen={isOpen}
          onClose={onClose}
          size={{ base: "sm", md: "md" }}
          isCentered
        >
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>{user.id === currentUser?.id ? "Your " : isFriendList ? "Friend's " : "User "} Information</ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
                <VStack
                    divider={<StackDivider borderColor='gray.200' />}
                    spacing={4}
                    align='stretch'
                >
                    <Container>
                        <Heading as='h2' size='sm'>{isFriendList ? "Friend's Name" : "User Name"}</Heading>
                        <Text fontSize='xl'>{user.full_name}</Text>
                    </Container>
                    <Container>
                        <Heading as='h2' size='sm'>{isFriendList ? "Friend's Email" : "User Email"}</Heading>
                        <Text fontSize='xl'>{user.email}</Text>
                    </Container>
                    <Container>
                        <Heading as='h2' size='sm'>{isFriendList ? "Friend's Status" : "User Status"}</Heading>
                        <Text fontSize='xl'>{user.status || "N/A"}</Text>
                    </Container>
                </VStack>
            </ModalBody>
  
            <ModalFooter gap={3}>
                {user.id !== currentUser?.id || !isFriendList &&
                    <Button
                        variant="primary"
                        type="submit"
                        onClick={() => sendRequest(user.id)}
                    >
                        Send Friend Request
                    </Button>
                }
              <Button onClick={onCancel}>Cancel</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </>
    )
  }
  
  export default ViewUser
  