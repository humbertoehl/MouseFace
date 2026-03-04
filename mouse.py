import pygame, sys
import cv2
import mediapipe as mp
import numpy as np
import random


pygame.init()
screen = pygame.display.set_mode((800,500))
pygame.display.set_caption('MouseFace')
clock = pygame.time.Clock()

capture = cv2.VideoCapture(0)


# Mediapipe face mesh
mp_face_mesh = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)





HEIGHT = screen.get_height()
WIDTH = screen.get_width()

CAM_WIDTH = 200
CAM_HEIGHT = 200
CAM_POS = (0,0)

mouse_img = pygame.image.load("mouse.png").convert_alpha()
mouse_img_left = pygame.transform.smoothscale(mouse_img, (48, 48))
mouse_img_right  = pygame.transform.flip(mouse_img_left, True, False)
mouse_rect = mouse_img_left.get_rect(center=(WIDTH//2, HEIGHT//2))
facing = 1

pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
vel = pygame.Vector2(0,0)

heart_img = pygame.image.load("heart.png").convert_alpha()
heart_img = pygame.transform.smoothscale(heart_img, (32, 32))
hearts = []

def create_hearts():
    spacing = 50
    for i in range (0,3):
        rect_heart = heart_img.get_rect(topleft=(int(CAM_WIDTH + spacing), 30))
        hearts.append({"rect_heart": rect_heart})
        spacing+=50

create_hearts()

INVULNERAVILITY_TIME = 3000
invulnerable_until = 0


cat_img = pygame.image.load("evil_cat.png").convert_alpha()
cat_img_left = pygame.transform.smoothscale(cat_img, (64, 64))
cats_left = []
SPAWN_MIN_MS = 1600
SPAWN_MAX_MS = 3500
next_spawn_ms = pygame.time.get_ticks() + random.randint(SPAWN_MIN_MS, SPAWN_MAX_MS)

CAT_SPEED_MIN = 4
CAT_SPEED_MAX = 9.5


# Physics for the mouse
GRAVITY = 0.8
HOR_ACCE = 0.8
MAX_HOR_SPEED = 9.0
HOR_FRICTION = 0.90

JUMP_SPEED = 18
is_on_ground = False

def hor_speed_limit(vel, low, high):
    return max(low, min(vel, high))



#game over logic
game_over = False
font_big = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 20)
restart_button = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 20, 240, 50)
quit_button = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 90, 240, 50)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            face_mesh.close()
            capture.release()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and is_on_ground:
                vel.y = -JUMP_SPEED
                is_on_ground = False


        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            pygame.display.update()
            clock.tick(60)
            if restart_button.collidepoint(event.pos):
                create_hearts()
                cats_left.clear()
                vel = pygame.Vector2(0,0)
                pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
                mouse_rect.center = pos
                game_over = False

            if quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
            continue

    ok, frame = capture.read()
    if not ok:
        continue

    #mirrored camera
    frame = cv2.flip(frame, 1)

    #mediapipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    # draw the mesh onto the frame
    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            # mp_draw.draw_landmarks(
            #     image=frame,
            #     landmark_list=landmarks,
            #     connections=mp_face_mesh.FACEMESH_TESSELATION,
            #     landmark_drawing_spec=None,
            #     connection_drawing_spec=mp_styles.get_default_face_mesh_tesselation_style(),
            # )
            h, w, _ = frame.shape

            upper_lip = (int(landmarks.landmark[13].x*w), int(landmarks.landmark[13].y*h))
            # cv2.circle(frame, upper_lip, 10, (0, 0, 255), -1)

            lower_lip = (int(landmarks.landmark[14].x*w), int(landmarks.landmark[14].y*h))
            # cv2.circle(frame, lower_lip, 10, (0, 0, 255), -1)

            upper_face = (int(landmarks.landmark[10].x*w), int(landmarks.landmark[10].y*h))
            # cv2.circle(frame, upper_face, 10, (0, 0, 255), -1)

            lower_face = (int(landmarks.landmark[152].x*w), int(landmarks.landmark[152].y*h))
            # cv2.circle(frame, lower_face, 10, (0, 0, 255), -1)

            nose_point = (int(landmarks.landmark[1].x*w), int(landmarks.landmark[1].y*h))
            # cv2.circle(frame, nose_point, 10, (0, 0, 255), -1)

            left_cheek = (int(landmarks.landmark[123].x*w), int(landmarks.landmark[123].y*h))
            # cv2.circle(frame, left_cheek, 10, (0, 0, 255), -1)

            right_cheek = (int(landmarks.landmark[352].x*w), int(landmarks.landmark[352].y*h))
            # cv2.circle(frame, right_cheek, 10, (0, 0, 255), -1)


    open_mouth_length = lower_lip[1]-upper_lip[1]
    face_height = lower_face[1]-upper_face[1]
    nose_leftcheek_length = nose_point[0]-left_cheek[0]
    nose_rightcheek_length = -nose_point[0]+right_cheek[0]
    # print(nose_leftcheek_length, nose_rightcheek_length)


    PROC_W, PROC_H = 200, 200

    little_camera_screen = cv2.resize(frame, (PROC_W, PROC_H), interpolation=cv2.INTER_AREA)
    little_camera_screen_rgb = cv2.cvtColor(little_camera_screen, cv2.COLOR_BGR2RGB)
    camera_surface = pygame.surfarray.make_surface(np.transpose(little_camera_screen_rgb, (1, 0, 2)))


    if open_mouth_length>20 and is_on_ground:
        vel.y = -JUMP_SPEED
        is_on_ground = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or nose_leftcheek_length<60:
        vel.x-=HOR_ACCE

    if keys[pygame.K_RIGHT] or nose_rightcheek_length<60:
        vel.x+=HOR_ACCE

    vel.x = hor_speed_limit(vel.x, -MAX_HOR_SPEED, MAX_HOR_SPEED)

    #friction for better feeling of movement
    if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
        vel.x *= HOR_FRICTION
        if abs(vel.x)<0.05:
            vel.x = 0
    if vel.x > 0.2:
        facing = -1
    elif vel.x < -0.2:
        facing = 1
    #gravity
    vel.y += GRAVITY

    #update pos
    pos += vel
    mouse_rect.center = (int(pos.x), int(pos.y))

    # floor collision
    if mouse_rect.bottom > HEIGHT:
        mouse_rect.bottom = HEIGHT
        pos.y = mouse_rect.centery
        vel.y = 0
        is_on_ground = True
    else:
        is_on_ground = False

    # side collisions
    if mouse_rect.right > WIDTH:
        mouse_rect.right = WIDTH
        pos.x = mouse_rect.centerx
        vel.x = 0

    if mouse_rect.left < 0:
        mouse_rect.left = 0
        pos.x = mouse_rect.centerx
        vel.x = 0


    #cat logic
    #spawning
    now = pygame.time.get_ticks()
    if now >= next_spawn_ms:
        y_cat =HEIGHT - cat_img_left.get_height()
        rect_cat_left = cat_img_left.get_rect(topleft=(WIDTH, y_cat))

        vx_cat_left = random.uniform(CAT_SPEED_MIN, CAT_SPEED_MAX)
        cats_left.append({"rect_cat_left": rect_cat_left, "vx_cat_left": vx_cat_left})

        next_spawn_ms = now + random.randint(SPAWN_MIN_MS, SPAWN_MAX_MS)

    #moving
    for c in cats_left:
        c["rect_cat_left"].x -= c["vx_cat_left"]

    # clenaing
    cats_left = [c for c in cats_left if c["rect_cat_left"].right > 0]

    now = pygame.time.get_ticks()
    #cat collision
    if now >= invulnerable_until:
        for c in cats_left:
            if mouse_rect.colliderect(c["rect_cat_left"]):
                if hearts:
                    hearts.pop()
                invulnerable_until = now + INVULNERAVILITY_TIME
                break
    
    if len(hearts)==0:
        game_over = True

    
    screen.fill((30,30,30)) #bg color
    screen.blit(camera_surface, CAM_POS)
    pygame.draw.rect(screen, (30, 30, 30), (*CAM_POS, CAM_WIDTH, CAM_HEIGHT), 2)

    for c in cats_left:
        screen.blit(cat_img_left, c["rect_cat_left"])
        # pygame.draw.rect(screen, (255, 0, 0), c["rect_cat_left"], 2)

    for h in hearts:
        screen.blit(heart_img, h["rect_heart"])

    mouse_img = mouse_img_left if facing == 1 else mouse_img_right

    now = pygame.time.get_ticks()
    invulnerable = now < invulnerable_until
    draw_mouse = (not invulnerable) or ((now // 100) % 2 == 0)
    if draw_mouse:
        screen.blit(mouse_img, mouse_rect)
    #pygame.draw.rect(screen, (255, 0, 0), mouse_rect, 2)


    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        text = font_big.render("The cats won :c", True, (255,255,255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80))

        pygame.draw.rect(screen, (200,200,200), restart_button)
        pygame.draw.rect(screen, (200,200,200), quit_button)

        restart_text = font_small.render("I will take revenge", True, (0,0,0))
        quit_text = font_small.render("I quit, the cats are better than me", True, (0,0,0))

        screen.blit(restart_text, (
            restart_button.centerx - restart_text.get_width()//2,
            restart_button.centery - restart_text.get_height()//2))

        screen.blit(quit_text, (
            quit_button.centerx - quit_text.get_width()//2,
            quit_button.centery - quit_text.get_height()//2))

    pygame.display.update()
    clock.tick(60)