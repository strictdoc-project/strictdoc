// @relation(SF_REQ-001, scope=file)
FUNCTION_BLOCK FB_Test
VAR_INPUT
	i_xA: BOOL;
	i_xB: BOOL;
END_VAR
VAR_OUTPUT
	o_xX: BOOL;
END_VAR

// --- BEGIN IMPLEMENTATION ---
// @relation(REQ-002, scope=range_start)
IF i_xA AND i_xB THEN
	o_xX := TRUE;
ELSE
	o_xX := FALSE;
END_IF
// @relation(REQ-002, scope=range_end)
