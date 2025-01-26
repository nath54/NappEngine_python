import glfw  # type: ignore
import vulkan as vk
import numpy as np
import ctypes
from freetype import Face  # type: ignore

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600



class VkExtent2D(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32)
    ]

class VkSurfaceCapabilitiesKHR(ctypes.Structure):
    _fields_ = [
        ("minImageCount", ctypes.c_uint32),
        ("maxImageCount", ctypes.c_uint32),
        ("currentExtent", VkExtent2D),
        ("minImageExtent", VkExtent2D),
        ("maxImageExtent", VkExtent2D),
        ("maxImageArrayLayers", ctypes.c_uint32),
        ("supportedTransforms", ctypes.c_uint32),
        ("currentTransform", ctypes.c_uint32),
        ("supportedCompositeAlpha", ctypes.c_uint32),
        ("supportedUsageFlags", ctypes.c_uint32),
    ]



# Vulkan initialization
class VulkanApp:
    def __init__(self):
        self.instance = None
        self.device = None
        self.queue = None
        self.surface = None
        self.swapchain = None
        self.command_pool = None
        self.command_buffers = None
        self.framebuffers = None
        self.render_pass = None

    def initialize(self, window):
        self.create_instance()
        self.create_surface(window)
        self.create_device()
        self.setup_swapchain()
        self.create_render_pass()
        self.create_framebuffers()

    def create_instance(self):
        # Query required extensions from GLFW
        glfw_extensions = glfw.get_required_instance_extensions()

        if not glfw_extensions:
            raise RuntimeError("GLFW failed to find required Vulkan extensions")

        # Define the application info
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="Vulkan GLFW Demo",
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_API_VERSION_1_0,
        )

        # Define the instance create info
        instance_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
            enabledExtensionCount=len(glfw_extensions),
            ppEnabledExtensionNames=glfw_extensions,
        )

        # Create the Vulkan instance
        self.instance = vk.vkCreateInstance(instance_info, None)

    def create_surface(self, window):
        # Ensure the Vulkan extensions are available in GLFW
        if not glfw.vulkan_supported():
            raise RuntimeError("GLFW Vulkan not supported")

        # Retrieve the Vulkan surface creation function from GLFW
        surface_ptr = ctypes.c_void_p()
        result = glfw.create_window_surface(self.instance, window, None, ctypes.byref(surface_ptr))

        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create Vulkan surface: {result}")

        self.surface = surface_ptr


    def create_device(self):
        physical_devices = vk.vkEnumeratePhysicalDevices(self.instance)
        physical_device = physical_devices[0]

        queue_family_index = 0  # Assuming the first queue family supports what we need

        device_queue_create_info = vk.VkDeviceQueueCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=queue_family_index,
            queueCount=1,
            pQueuePriorities=[1.0]
        )

        device_info = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=device_queue_create_info
        )

        self.device = vk.vkCreateDevice(physical_device, device_info, None)
        self.queue = vk.vkGetDeviceQueue(self.device, queue_family_index, 0)

    def setup_swapchain(self):
        # Ensure surface is valid
        if not hasattr(self, "surface") or not self.surface:
            raise RuntimeError("Vulkan surface is not initialized")

        # Load vkGetPhysicalDeviceSurfaceCapabilitiesKHR
        vkGetPhysicalDeviceSurfaceCapabilitiesKHR = vk.vkGetInstanceProcAddr(
            self.instance, "vkGetPhysicalDeviceSurfaceCapabilitiesKHR"
        )

        if not vkGetPhysicalDeviceSurfaceCapabilitiesKHR:
            raise RuntimeError("Failed to load vkGetPhysicalDeviceSurfaceCapabilitiesKHR")

        # Define the argument and return types
        vkGetPhysicalDeviceSurfaceCapabilitiesKHR.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(VkSurfaceCapabilitiesKHR)
        ]
        vkGetPhysicalDeviceSurfaceCapabilitiesKHR.restype = ctypes.c_int  # VkResult

        # Query surface capabilities
        surface_capabilities = VkSurfaceCapabilitiesKHR()
        result = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(
            self.physical_device, self.surface, ctypes.byref(surface_capabilities)
        )

        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to query surface capabilities: {result}")

        # Set the extent (window size)
        extent = surface_capabilities.currentExtent

        # Log debug info
        print(f"Surface: {self.surface}, Extent: {extent.width}x{extent.height}")

        # Swapchain create info
        swapchain_info = vk.VkSwapchainCreateInfoKHR(
            sType=vk.VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
            surface=self.surface,
            minImageCount=2,
            imageFormat=vk.VK_FORMAT_B8G8R8A8_SRGB,
            imageColorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR,
            imageExtent=extent,
            imageArrayLayers=1,
            imageUsage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            queueFamilyIndexCount=0,
            pQueueFamilyIndices=None,
            preTransform=surface_capabilities.currentTransform,
            compositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode=vk.VK_PRESENT_MODE_FIFO_KHR,
            clipped=vk.VK_TRUE,
            oldSwapchain=vk.VK_NULL_HANDLE
        )

        # Create the swapchain
        self.swapchain = vk.vkCreateSwapchainKHR(self.device, swapchain_info, None)





    def create_render_pass(self):
        #
        color_attachment = vk.VkAttachmentDescription(
            format=vk.VK_FORMAT_B8G8R8A8_SRGB,
            samples=vk.VK_SAMPLE_COUNT_1_BIT,
            loadOp=vk.VK_ATTACHMENT_LOAD_OP_CLEAR,
            storeOp=vk.VK_ATTACHMENT_STORE_OP_STORE,
            stencilLoadOp=vk.VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp=vk.VK_ATTACHMENT_STORE_OP_DONT_CARE,
            initialLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout=vk.VK_IMAGE_LAYOUT_PRESENT_SRC_KHR
        )

        color_attachment_ref = vk.VkAttachmentReference(
            attachment=0,
            layout=vk.VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
        )

        subpass = vk.VkSubpassDescription(
            pipelineBindPoint=vk.VK_PIPELINE_BIND_POINT_GRAPHICS,
            colorAttachmentCount=1,
            pColorAttachments=[color_attachment_ref]
        )

        render_pass_info = vk.VkRenderPassCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
            attachmentCount=1,
            pAttachments=[color_attachment],
            subpassCount=1,
            pSubpasses=[subpass]
        )

        self.render_pass = vk.vkCreateRenderPass(self.device, render_pass_info, None)

    def record_command_buffer(self, command_buffer, framebuffer):
        #
        begin_info = vk.VkCommandBufferBeginInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO
        )

        vk.vkBeginCommandBuffer(command_buffer, begin_info)

        clear_color = vk.VkClearValue(color=[[0.0, 0.0, 0.0, 1.0]])  # Black background
        render_pass_info = vk.VkRenderPassBeginInfo(
            sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
            renderPass=self.render_pass,
            framebuffer=framebuffer,
            renderArea=vk.VkRect2D(offset=(0, 0), extent=(WINDOW_WIDTH, WINDOW_HEIGHT)),
            clearValueCount=1,
            pClearValues=[clear_color]
        )

        vk.vkCmdBeginRenderPass(command_buffer, render_pass_info, vk.VK_SUBPASS_CONTENTS_INLINE)
        vk.vkCmdEndRenderPass(command_buffer)

        vk.vkEndCommandBuffer(command_buffer)

    def create_framebuffers(self):
        #
        swapchain_images = vk.vkGetSwapchainImagesKHR(self.device, self.swapchain)

        self.framebuffers = []
        for image in swapchain_images:
            image_view = vk.vkCreateImageView(self.device, vk.VkImageViewCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                image=image,
                viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
                format=vk.VK_FORMAT_B8G8R8A8_SRGB,
                components=vk.VkComponentMapping(),  # Identity mapping
                subresourceRange=vk.VkImageSubresourceRange(
                    aspectMask=vk.VK_IMAGE_ASPECT_COLOR_BIT,
                    baseMipLevel=0,
                    levelCount=1,
                    baseArrayLayer=0,
                    layerCount=1,
                )
            ), None)

            framebuffer = vk.vkCreateFramebuffer(self.device, vk.VkFramebufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                renderPass=self.render_pass,
                attachmentCount=1,
                pAttachments=[image_view],
                width=WINDOW_WIDTH,
                height=WINDOW_HEIGHT,
                layers=1
            ), None)

            self.framebuffers.append(framebuffer)

    def cleanup(self):
        vk.vkDestroyInstance(self.instance, None)

# GLFW window setup
def main():
    if not glfw.init():
        print("Failed to initialize GLFW")
        return

    glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Vulkan + GLFW Demo", None, None)

    if not window:
        print("Failed to create GLFW window")
        glfw.terminate()
        return

    # Initialize Vulkan
    vulkan_app = VulkanApp()
    vulkan_app.initialize(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Acquire image from swapchain
        image_index = vk.vkAcquireNextImageKHR(
            vulkan_app.device, vulkan_app.swapchain, vk.UINT64_MAX, None, None
        )

        # Submit rendering commands (placeholder for now)
        submit_info = vk.VkSubmitInfo(
            sType=vk.VK_STRUCTURE_TYPE_SUBMIT_INFO,
            commandBufferCount=1,
            pCommandBuffers=[vulkan_app.command_buffers[image_index]]
        )
        vk.vkQueueSubmit(vulkan_app.queue, 1, submit_info, None)

        # Present the image
        present_info = vk.VkPresentInfoKHR(
            sType=vk.VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
            swapchainCount=1,
            pSwapchains=[vulkan_app.swapchain],
            pImageIndices=[image_index]
        )
        vk.vkQueuePresentKHR(vulkan_app.queue, present_info)

    vulkan_app.cleanup()
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
