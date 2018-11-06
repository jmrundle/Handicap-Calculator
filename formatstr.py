def format_str(string, split=False, limit=15):
    final = ""
    line_length = 0

    for word in string.split(" "):
        if line_length + len(word) < limit:
            final += word + ' '
            line_length += len(word) + 1

        elif line_length + len(word) > limit:
            if line_length + len(word) < limit + 2:
                final += word + '\n'
                line_length = 0
            elif line_length + 2 >= limit:
                final += '\n' + word + ' '
                line_length = len(word) + 1
            else:
                if split:
                    end = limit - line_length - 1
                    final += word[: end] + "-\n"
                    new = word[end:]
                    final += format_str(new, split=True, limit=limit)
                    line_length = len(final.split('\n')[-1])
                else:
                    if len(word) > limit:
                        final += word + '\n'
                    else:
                        final += '\n' + word + ' '
                        line_length = len(word) + 1

        else:
            final += word + '\n'
            line_length = 0

    return final

msg = 'Aquickbr wnfo psoverth jhgfdsdfghjkjhgf asdkf dfdfggg asdfgdfsdafs asldf dfdfkj fjsdf dfksdf efkkncnjd eddf.'
print(format_str(msg, limit=15))
print(format_str(msg, split=True, limit=15))