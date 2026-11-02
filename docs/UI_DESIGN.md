# UI Design Specification: FaceMark (FRCAS)

**Product Name:** FaceMark (Face Recognition Classroom Attendance System)  
**Design Vision:** A lecturer takes attendance for 60+ students in under 45 seconds with zero manual roll calling and zero proxy attendance. The UI feels calm, enterprise-grade, fast, and trustworthy—comparable to modern tools from Linear, Apple, and Stripe.

---

## 1. Core Design Principles

| Principle | UI Translation |
|---|---|
| **Speed First** | 3-step linear flow: **① Live Scan ─── ② Review ─── ③ Finalize**. Completed in under 60 seconds. |
| **Zero File Upload Friction** | Fully camera-native. Both professor and student scan faces live via webcam/phone camera; file upload is only an optional fallback. |
| **Teacher in Control** | The AI suggests matches with confidence scores; the teacher can confirm, reassign, or override any detection with a single tap or keyboard shortcut. |
| **Visible Confidence** | No hidden black-box magic. Clear color codes, exact similarity percentages, and side-by-side face comparisons. |
| **Unlimited Room Coverage** | Teachers can snap as many sector photos/angles as needed (Front, Back Benches, Left/Right Wings, Corners) so backbenchers are never missed. |
| **DPDP Act Trust & Privacy** | Plain-language consent badges, biometric encryption indicators, and one-tap student data deletion ("Right to be Forgotten"). |

---

## 2. Design System & Tokens

### 2.1 Color Palette

#### Brand & Neutrals
| Token | Light Mode | Dark Mode | Application |
|---|---|---|---|
| `--primary` | `#4F46E5` (Indigo 600) | `#6366F1` (Indigo 500) | Primary CTA buttons, active tabs, focus rings |
| `--primary-hover` | `#4338CA` (Indigo 700) | `#4F46E5` (Indigo 600) | Hover and pressed states |
| `--bg` | `#F8FAFC` (Slate 50) | `#0B0F19` (Deep Navy) | App shell background |
| `--surface` | `#FFFFFF` (Pure White) | `#111827` (Slate 900) | Cards, modals, sidebars |
| `--surface-alt` | `#F1F5F9` (Slate 100) | `#1E293B` (Slate 800) | Table headers, secondary buttons, inputs |
| `--border` | `#E2E8F0` (Slate 200) | `#334155` (Slate 700) | Card borders, dividers |
| `--text-main` | `#0F172A` (Slate 900) | `#F8FAFC` (Slate 50) | Headings and primary body copy |
| `--text-muted` | `#64748B` (Slate 500) | `#94A3B8` (Slate 400) | Labels, hints, timestamps |

#### Status & Confidence Colors (Dual-Threshold Safety Net)
| Token | Hex | Badge Label | Match Criteria (ArcFace Cosine Similarity) | Meaning |
|---|---|---|---|---|
| `--status-present` | `#16A34A` (Emerald 600) | `Auto-Present` | $\text{Similarity} \ge 0.60$ (60%+) | Confirmed match, auto-marked present |
| `--status-review` | `#D97706` (Amber 600) | `Needs Review` | $0.40 \le \text{Similarity} < 0.60$ (40% - 59%) | Borderline similarity, requires teacher click |
| `--status-absent` | `#DC2626` (Rose 600) | `Absent` | Not detected in any photo | Registered student not seen in class |
| `--status-unknown` | `#0284C7` (Sky 600) | `Unknown Face` | $\text{Similarity} < 0.40$ (<40%) | Unregistered visitor or guest student |

> [!IMPORTANT]
> **Threshold Calibration Note:** Earlier drafts cited an 85% threshold. With 512-D ArcFace unit vectors, $\ge 0.60$ cosine similarity represents $>99.5\%$ verification confidence. A rigid 85% threshold would needlessly flag true students as review items. The calibrated thresholds are: $\ge 0.60$ for auto-present, $0.40 - 0.59$ for review, and $<0.40$ for unknown.

---

### 2.2 Typography

* **Primary Sans:** `Inter`, system-ui, -apple-system, sans-serif
* **Monospace (USN, Timestamps, Codes):** `JetBrains Mono`, monospace

| Hierarchy | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| Display H1 | 30px / 1.875rem | 700 (Bold) | 1.2 | Page titles, hero headers |
| H2 | 22px / 1.375rem | 600 (Semibold) | 1.3 | Card and section titles |
| H3 | 16px / 1.0rem | 600 (Semibold) | 1.4 | Component headers, modal titles |
| Body | 14px / 0.875rem | 400 (Regular) | 1.5 | Primary readable text |
| Caption / Small | 12px / 0.75rem | 500 (Medium) | 1.4 | Badges, labels, helper hints |
| USN Code | 13px / 0.8125rem | 600 (Semibold) | 1.2 | University Seat Numbers (e.g., `1MS21CS042`) |

---

### 2.3 Spacing, Elevation & Motion

* **Radius Tokens:** Small elements `8px` (`rounded-lg`), Cards `16px` (`rounded-2xl`), Modals & Viewfinder `24px` (`rounded-3xl`), Chips `9999px` (`rounded-full`).
* **Shadow Tokens:**
  * Subtle: `0 1px 3px rgba(15, 23, 42, 0.06)`
  * Card Elevation: `0 4px 20px -2px rgba(15, 23, 42, 0.08)`
  * Floating Modal: `0 20px 40px -4px rgba(15, 23, 42, 0.25)`
* **Micro-Interactions:**
  * Camera Shutter: 120ms white flash + synthesized audio click (`AudioContext`).
  * Face Detection Bounding Boxes: Smooth stagger in with spring scale `0.95 -> 1.0`.
  * Review Decision: Instant swap from review queue to confirmed grid with subtle green border pulse.
  * Finalize Celebration: Success checkmark animation with time-saved badge (`"Saved in 42s"`).

---

## 3. Two Dedicated Portal Experiences

### 3.1 Professor Portal (`/professor` or `/`)
Built for lecturers during busy class transitions.

1. **Dashboard Home View:**
   * Greeting: *"Good morning, Professor 👋"*
   * Hero Card: Next Scheduled Lecture (e.g. `Machine Learning · Section 6A`) with direct **`[ ▶ Start Attendance ]`** CTA.
   * Executive Metric Tiles:
     * **92.4%** Average Section Attendance
     * **14** Sessions this week
     * **3** Students below 75% attendance threshold (with quick alert list)
     * **48s** Average time to record attendance
2. **Attendance Workflow (The 3-Step Flow):**
   * **Step 1: Live Classroom Camera Scanner (Unlimited Snaps)**
     * Rear/front camera switch toggle (`🔄`).
     * Live alignment grid overlay with live photo counter (`"4 Photos Snapped"`).
     * Shutter button + preset sector pills (`Front Rows`, `Back Benches`, `Left Wing`, `Center`, `Right Wing`).
     * Dynamic thumbnail gallery of snapped photos with individual delete (`✖`) and clear all.
     * Large CTA: **`[ 🚀 Run AI Attendance on All (N) Photos ]`**
   * **Step 2: Interactive 2-Panel Review Screen (Hero Experience)**
     * **Left Panel:** Annotated classroom photo with interactive color-coded face bounding boxes (Auto-Present, Needs Review, Unknown). Photo selector tabs allow flipping through all captured room angles.
     * **Manual Override & Quick Add Toolbar:**
       * Dedicated toolbar positioned directly above review tabs.
       * **Roster Mode:** Select any student from the class roster and click **[+ Add to Attendance Sheet]** to mark them Present immediately.
       * **Custom Entry Mode:** Quickly input any USN & Student Name (for walk-in students or late arrivals) to add them directly to the attendance sheet.
     * **Right Panel:** Tabbed review list:
       * [ Needs Review (N) ]: Displays face crop, confidence score, and one-tap [ Confirm Present ] / [ Mark Absent ].
       * [ Confirmed Present (M) ]: Grid of present students with AI Match or Manual Override badges, plus one-tap [ Mark Absent ] revert option.
       * [ Absent (K) ]: Unmatched registered students, each equipped with a prominent green **[+ Add to Attendance Sheet]** button.
   * **Step 3: Save & Confirmation**
     * Celebratory summary card with attendance statistics and time saved.
     * 1-Click **[ Download Excel Report (.xlsx) ]**: Generated as a two-sheet college-ready workbook:
       * **Sheet 1 (Session Attendance):** Formatted session records with Date, Subject, Section, Student USN, Student Name, Status, and clear Verification Method (AI Facial Recognition vs. Teacher Manual Override).
       * **Sheet 2 (Cumulative Summary):** Semester-to-date attendance metrics, overall percentage, and automatic eligibility warning alerts flagged in soft red for students below 75%.
     * Direct **[ Download CSV ]** for ERP data sync.
3. **Student Roster & DPDP Privacy Tab:**
   * Filterable student directory by section.
   * Total enrolled facial angles counter (e.g. `3 Angles Enrolled`).
   * Permanent biometric deletion button with confirmation dialog.
4. **Reports & History Tab:**
   * Historical session log with date, present count, absent count, and attendance percentage.
   * Color-coded attendance rate badges (Green $\ge 75\%$, Red $< 75\%$).

---

### 3.2 Student Portal (`/student`)
Dedicated self-service face enrollment portal for students on smartphones or lab computers.

1. **Step 1: Identity & DPDP Consent:**
   * Inputs for USN, Full Name, and Section.
   * Plain-language biometric consent checkbox detailing data encryption and right-to-be-forgotten rights.
2. **Step 2: Studio Biometric Face Scanner (Zero File Uploads):**
   * Sleek dark-mode biometric HUD viewfinder.
   * Oval head-guide reticle with animated scanning sweep.
   * 3-Step Guided Motion Scanner:
     * 👤 **Pose 1: Look Straight (Center, 0°)**
     * 👈 **Pose 2: Turn Head Slightly Left (~20°)**
     * 👉 **Pose 3: Turn Head Slightly Right (~20°)**
   * Real-time audio-visual snap feedback.
   * 3-slot preview tray with individual retake options.
3. **Step 3: Verification & Success:**
   * Automatic ArcFace 512-D vector generation.
   * Confirmation badge: *"Face Enrolled: 3/3 Angles Active"*.

---

## 4. Accessibility & Responsive Matrix

* **Responsive Breakpoints:**
  * **Desktop (1024px+):** Full 2-panel side-by-side review interface with synchronized bounding box inspector.
  * **Tablet (768px - 1023px):** Stacked view (Classroom photo canvas on top, review list below).
  * **Mobile (<768px):** Phone-optimized camera viewfinder, swipeable review cards, thumb-friendly 48px touch targets.
* **Keyboard Shortcuts for Rapid Review:**
  * `Enter` / `Space`: Confirm focused review item as Present.
  * `X`: Reject review item / mark as Absent.
  * `Tab` / `Shift+Tab`: Cycle through review cards.
* **Accessibility (WCAG 2.2 AA):**
  * All status states convey meaning via **icon + text label + color** (never color alone).
  * Minimum touch target size: $44 \times 44\text{ px}$.
  * Focus indicators: `ring-2 ring-indigo-500 ring-offset-2`.
