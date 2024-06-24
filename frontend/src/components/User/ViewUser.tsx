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
  }
  
  const ViewUser = ({ user, isOpen, onClose }: ViewUserProps) => {
    const queryClient = useQueryClient()
    const showToast = useCustomToast()
    const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  
    // const {
    //   register,
    //   handleSubmit,
    //   reset,
    //   getValues,
    //   formState: { isSubmitting },
    // } = useForm<UserUpdateForm>({
    //   mode: "onBlur",
    //   criteriaMode: "all",
    //   defaultValues: user,
    // })
  
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
            <ModalHeader>{user.id === currentUser?.id ? 'Your ' : 'User '} Information</ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
                <VStack
                    divider={<StackDivider borderColor='gray.200' />}
                    spacing={4}
                    align='stretch'
                >
                    <Container>
                        <Heading as='h2' size='sm'>User Name</Heading>
                        <Text fontSize='xl'>{user.full_name}</Text>
                    </Container>
                    <Container>
                        <Heading as='h2' size='sm'>User Email</Heading>
                        <Text fontSize='xl'>{user.email}</Text>
                    </Container>
                    <Container>
                        <Heading as='h2' size='sm'>User Role</Heading>
                        <Text fontSize='xl'>{user.is_superuser ? 'Admin' : 'User'}</Text>
                    </Container>
                </VStack>
            </ModalBody>
  
            <ModalFooter gap={3}>
                {user.id !== currentUser?.id &&
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
  