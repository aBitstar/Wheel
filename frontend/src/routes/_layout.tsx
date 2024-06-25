import { Flex, Spinner } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

import Sidebar from "../components/Common/Sidebar"
import UserMenu from "../components/Common/UserMenu"
import useAuth, { isLoggedIn } from "../hooks/useAuth"

import WebSocketService from "../client/services/WebSocket"
import useCustomToast from "../hooks/useCustomToast"
import { useEffect } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { UserPublic } from "../client"



export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  const { isLoading  } = useAuth()
  const showToast = useCustomToast()
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  useEffect(() => {
    if (currentUser?.id) {
      const websocket = WebSocketService.connect(currentUser.id);
      if (websocket) {
        websocket.onmessage = (event: any) => {
        showToast("Success!", event.data, "info");
        };
      }
    }

    return () => {
        WebSocketService.disconnect();
    };
  }, [currentUser?.id]);

  return (
    <Flex maxW="large" h="auto" position="relative">
      <Sidebar />
      {isLoading ? (
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" color="ui.main" />
        </Flex>
      ) : (
        <Outlet />
      )}
      <UserMenu />
    </Flex>
  )
}
